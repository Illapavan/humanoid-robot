from flask import jsonify
from utils.session_util import SessionManager
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

session_manager = SessionManager()

def new_session():
    session_id = session_manager.create_session()
    response_data = {
        "session_id": session_id
    }

    return jsonify(response_data)

def testRoute():
        db_connection = mysql.connector.connect(
        host=os.getenv('DBADDRESS'),
        port = os.getenv('DBPORT'),
        user=os.getenv('DBUSERNAME'),
        password=os.getenv('DBPASSWORD'),
        database=os.getenv('DBNAME')
        )

        cursor = db_connection.cursor()
        query = "select * from signup_and_login_table where id = 10026993" 

        cursor.execute(query)

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Process the fetched data
        for row in rows:
            print(row)

        cursor.close()
        db_connection.close()

        response_data = {
            "response":"working fine"
        }
        return jsonify(response_data)    