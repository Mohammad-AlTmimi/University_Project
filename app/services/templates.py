import os
from dotenv import load_dotenv
from fastapi import HTTPException
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)
from app.nodatabase import get_nodb
def calculateValue(payload):
    try:    
        SEMESTER = int(os.getenv('semester'))
        course_type_weight = {
            'متطلب جامعة اجباري': 60,
            'متطلب جامعة اختياري': 50,
            'متطلب كلية اجباري': 90,
            'متطلب تخصص اجباري': 100,
            'متطلب تخصص اختياري': 80,
            'مساقات حرة': 0
        }
        currentWeight = course_type_weight[payload['course_type']]
        for sem in payload[-1]:
            currentWeight -= abs(SEMESTER - int(sem) if sem.isdigit() else 0) * 5
    
        return currentWeight

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
async def buildTableTemplate(payload):
    try:
        mongodb = await get_nodb()
        db_user_data = mongodb['student_data']
        db_availabe_course = mongodb['semester_courses']
        user_data_cursor = db_user_data.find({'portal_id': payload.portal_id})
        availabe_course_cursor = db_availabe_course.find({'active': True})

        user_data = await user_data_cursor.to_list(length=None)
        availabe_course = await availabe_course_cursor.to_list(length=None)

        admin_course = {}
        for element in availabe_course['courses']:
            couser_code = element[0]
            course_info = element[1:]
            admin_course[course_code].append(course_info)
            
        user_course = []
        user_available_course = []
        for category in user_data['courses']:
            for course in category['courses']:
                user_code = course[0]
                user_course[user_code] = course[1:]
        
        for category in user_data['courses']:
            if category['remaining_hours'] == 0:
                continue
            for course in category['courses']:
                e = True
                course_code = course[0]
                if course_code not in admin_course:
                    continue
                for relatedCourse in course[-1]:
                    if user_course[relatedCourse][2] == '' or user_course[relatedCourse][2] == 'مسجل':
                        e = False
                        break
                if not e:
                    continue
                for entry in admin_course[course_code]:
                    entry['course_type'] = category['course_type']
                    entry['Priority'] = calculateValue({
                        **entry,
                        'course_type': category['course_type'],
                        'related_semesters': course[-1]
                    })
                    user_available_course.append(entry)
        print(user_available_course)
        
        return 
    except Exception as e:
        raise e
