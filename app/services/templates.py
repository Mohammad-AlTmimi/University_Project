import os
from dotenv import load_dotenv
from fastapi import HTTPException
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)
from app.nodatabase import get_nodb
from collections import defaultdict
from typing import Dict, Any
import json
from app.database import get_db
from app.nodatabase import get_nodb
from sqlalchemy.future import select
from app.models.user import User, UserUpdate
templates = {
    'Build Table': """
    {User_Info}
You are MiLo (Mind Logic), a smart assistant for Hebron University students.
Your task is to generate a semester schedule based on the given courses and user preferences.
Only respond to questions specifically related to Hebron University, such as departments, schedules, professors, and campus services. If the question is not related to Hebron University, politely reply with: 'I'm sorry, I can only help with questions related to Hebron University
### Thought Process:
1. Answer the user's question in the same language the question is asked, whether it's Arabic or English.
The course content may be in Arabic or English, but your response language should always match the language of the question.

2. Extract the **required semester** and **student's preferences** (like specific courses or time preferences) from the question.

3. Identify the matching **courses** based on the semester.

4. **Rules to follow strictly**:
   - **No time conflicts**: Courses must not overlap in their scheduled times.
   - **No duplicate courses**: 
     - If the same course (by Course Name or Course Code) appears more than once at different times, select **only one**.
     - Choose the version that best fits the student's preferences or has the highest priority.
     - After building the schedule, **double-check** that no course is listed more than once.
   - **Priority Order**:
     1. First, **respect the student's requests** exactly as they asked.
     2. Then, use the **Priority** field to choose the best available option.

5. Format the selected courses into a **structured table** with:
   - Course Name  
   - Course Code (or Class Number)  
   - Instructor  
   - Time & Location  

6. If any required information is missing or unclear, politely ask the student for clarification.

7. Always present the output neatly in **table format**.

8. **Important: At the end, recheck the final list to ensure no duplicate Course Names or Course Codes appear.**

9. If the user's request cannot be fully satisfied (e.g., the student asks for 19 credit hours, but available courses only allow 15 due to conflicts or limited availability), do the following:

Fulfill as much of the request as possible within the given constraints.

Clearly and politely inform the student of the limitation, explaining why the full request couldn’t be achieved.

Suggest helpful alternatives or next steps, such as:

Relaxing some preferences (e.g., instructor or time).

Considering additional or alternative courses.

Taking remaining hours in a future semester.

### Available Courses for Student:
{user_available_course}

### Student Question:
""",
'Guest User':
"""
You are chatting with a guest user. They do not have an account and may ask general questions.
Treat the user respectfully and assume they are unfamiliar with internal systems.
""",
'Student':
    """
You are chatting with a {student_name}. He is a {student_level} Year in University , His Cumulative GPA is {GPA} out of Hundred, and he is {Under_warning} Under Warning, User Study in College of Information Technology Computer science major.
    """
}




def calculateValue(payload: dict) -> float:
    try:
        course_type_weight = {
            'متطلب جامعة اجباري': 60,
            'متطلب جامعة اختياري': 50,
            'متطلب كلية اجباري': 90,
            'متطلب تخصص اجباري': 100,
            'متطلب تخصص اختياري': 80,
            'مساقات حرة': 0
        }
        currentWeight = course_type_weight.get(payload['course_type'], 0)
        
        return currentWeight
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate priority: {str(e)}")  


async def buildTableTemplate(payload):
    try:
        mongodb = await get_nodb()
        db_user_data = mongodb['student_data']
        db_availabe_course = mongodb['semester_courses']
        user_data_cursor = db_user_data.find({'portal_id': payload.portal_id}).sort('create_time', -1)
        availabe_course_cursor = db_availabe_course.find().sort('create_time', -1).limit(1)

        user_data = await user_data_cursor.to_list(length=None)
        availabe_course = await availabe_course_cursor.to_list(length=None)

        if not user_data:
            raise ValueError(f"No user data found for portal_id: {payload.portal_id}")
        if not availabe_course:
            raise ValueError("No active courses found")

        course_doc = availabe_course[0]
        user_data = user_data[0]

        if 'courses' not in course_doc:
            raise ValueError("No courses field in the newest active course")

        admin_course = defaultdict(list)
        for element in course_doc['courses']:
            if 'CRS_NO' not in element:
                raise ValueError(f"Missing CRS_NO in course data: {element}")
            course_code = element['CRS_NO']
            course_info = {k: v for k, v in element.items() if k != 'CRS_NO'}
            admin_course[course_code].append(course_info)

        # Build user_course: Maps CRS_NO to course details [name, credits, status, ?, prerequisites]
        user_course = {}  # Initialize as dict
        for category in user_data['courses']:
            for course in category['courses']:
                user_code = course[0]  # CRS_NO
                user_course[user_code] = course[1:]

        user_available_course = []
        for category in user_data['courses']:
            if category['remaining_hours'] == 0:
                continue
            for course in category['courses']:
                e = True
                course_code = course[0]
                if course_code not in admin_course:
                    continue
                # Check prerequisites
                for relatedCourse in course[-1]:
                    if relatedCourse and (relatedCourse not in user_course or
                                        user_course[relatedCourse][2] not in ['ناجح']):
                        e = False
                        break
                if not e:
                    continue
                # Add available courses with additional metadata
                for entry in admin_course[course_code]:
                    entry_copy = entry.copy()  # Avoid modifying original
                    entry_copy['course_type'] = category['course_type']
                    entry_copy['Priority'] = calculateValue({
                        **entry_copy,
                        'course_type': category['course_type'],
                        'related_semesters': course[-1]
                    })
                    entry_copy['Credit Hours'] = course[2]
                    entry_copy['Course ID'] = course_code
                    user_available_course.append(entry_copy)

        formatted_admin_course = json.dumps(dict(admin_course), ensure_ascii=False, indent=2)
        formatted_user_course = json.dumps(user_course, ensure_ascii=False, indent=2)
        formatted_user_available_course = json.dumps(user_available_course, ensure_ascii=False, indent=2)

        final_template = templates['Build Table'].format(
            user_available_course=formatted_user_available_course,
            User_Info = await userGeneralInfo(user_id = payload.user_id , portal_id = payload.portal_id)
        )
        
        return final_template

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise ValueError(f"Failed to build table template: {str(e)}")

async def userGeneralInfo(user_id, portal_id):
    if user_id == 'guest' or portal_id == 'guest':
        return templates['Guest User']
    
    mongodb = await get_nodb()
    
    async for db in get_db(): 
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()  # Get the user or None

        db_user_data = mongodb['student_data']
        user_data_cursor = db_user_data.find({'portal_id': portal_id}).sort('create_time', -1)
        user_data_list = await user_data_cursor.to_list(length=1)
        user_data = user_data_list[0] if user_data_list else None

        if not user_data or not user:
            return templates['Guest User']

        # Format the response based on the retrieved data
        print(user_data)
        template = templates['Student'].format(
            student_name=user.name,
            student_level=user_data['level'],
            GPA=user_data['GPA'],
            Under_warning='**is**' if user_data['under_warning'] else '**is not**'
        )

        # Check for update status
        if user.updated == UserUpdate.No:
            template += (
                '\n\nStudent Information May Not Be Updated. '
                'You should warn the student that they may need to update their portal password on the MiLo website.\n\n'
            )

        return template


            

        
    

async def generalQuestionTemplate(payload):
    return