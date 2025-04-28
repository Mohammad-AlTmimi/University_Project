import os
from dotenv import load_dotenv
from fastapi import HTTPException
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)
from app.nodatabase import get_nodb
from collections import defaultdict
from typing import Dict, Any

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
        user_data_cursor = db_user_data.find({'portal_id': payload.portal_id})
        availabe_course_cursor = db_availabe_course.find().sort('create_time', -1).limit(1)

        user_data = await user_data_cursor.to_list(length=None)
        availabe_course = await availabe_course_cursor.to_list(length=None)

        # Check if data exists
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
                for relatedCourse in course[-1]:  # course[-1] is prerequisites list
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
                    user_available_course.append(entry_copy)
        print(user_available_course)
        return {
            'admin_course': dict(admin_course),
            'user_course': user_course,
            'user_available_course': user_available_course
        }

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise ValueError(f"Failed to build table template: {str(e)}")