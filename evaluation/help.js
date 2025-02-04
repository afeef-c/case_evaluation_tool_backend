// add company and admins (by Super admin)
 let compData = {
    "name": "company1",
    
    "admins": [
      {
        "username": "admin1",
        "password": "adminpass1"
      },
      {
        "username": "admin2",
        "password": "adminpass2"
      }
    ]
  }
  
// add admin to company
let adminData={
    "username": "new_admin",
    "password": "newadminpass"
  }
  

//add staff by company admin
let staff_data={
    "name": "Staff1",
    "username": "staff1",
    "password": "staff1"
  }


//by client(admin)
//Add case evaluation form fields
let fieldsData = {
    "field_options": [
        {
            "name": "Physical Injury",
            "options": [
                {
                    "name": "Significant/Severe",
                    "description": "testt tjtetheht h rerhehrerierherehrer"
                },
                {
                    "name": "Standard",
                    "description": "testt tjtereretheht h fererre"
                }
            ]
        },
        {
            "name": "Treatment",
            "options": [
                {
                    "name": "Immediate and ongoing",
                    "description": "fgdgd tjtetheht h gdggdgd"
                },
                {
                    "name": "Immediate only, but willing to treat",
                    "description": "wewewew wewewe ewewh fererre"
                }
            ]
        }
    ],
    "case_evaluation_options": [
        {
            "name": "Signed",
            "description": "fgdgd tjtetheht h gdggdgd"
        },
        {
            "name": "Declined",
            "description": "wewewew wewewe ewewh fererre"
        }
    ]
}

//Add case evaluation rules
let rulesData = {
    userId : 1,
    field_options: [
        {
            name: "Physical Injury",
            option: "Significant/Severe"
        },
        {
            name: "Treatment",
            option: "Immediate and ongoing"
        },
    ],
    case_evaluation: "Signed"
}


//Add pdf Template Fields
let templateData = {
    userId : 1,
    logo_img: "",
    color: "#062135",
    footer_email: "test@gmial.com",
    footer_phone: "1234567890"
}




let clientRes= {
    "client_name": "John Doe",
    "client_email":"john@gmail.com",
    "client_phone":"7652432321",
    "company":2,
    "responses": [
        {
            "field_id": 1,
            "option": "Significant/Severe"
        },
        {
            "field_id": 2,
            "option": "Immediate and ongoing"
        }
    ]
}  


//respose after first submission

{
    "id": 1,
    "client_name": "John Doe",
    "client_email": "john@gmail.com",
    "client_phone": "7652432321",
    "is_submitted": false,
    "pdf_file": null
}


