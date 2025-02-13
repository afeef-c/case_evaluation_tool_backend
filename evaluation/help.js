// add company and admins (by Super admin)
 let compData = {
    "company_name": "company1",
    "name":"admin1",
    "username": "admin1",
    "password": "adminpass1"
      
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
        },
        {
            "name": "Case Evaluation",
            "options": [
                {
                    "name": "Signed",
                    "description": "fgdgd tjtetheht h gdggdgd"
                },
                {
                    "name": "Declined",
                    "description": "wewewew wewewe ewewh fererre"
                }
            ]
        },

        // for udpate field and options with id will update existing data
        {
            "id": 19,
           "name": "Physical Injury1.1",
           "options": [
               {   
                   "id":37,
                   "name": "Significant",
                   "description": "testt tjtetheht h rerhehrerierherehrer"
               },
               {
                   "name": "New Standard ",
                   "description": "testt tjtereretheht h fererre"
               }
           ]
       }

    ]
    
}


//Add case evaluation rules
let rulesData = {
    
    "field_options": [
        {
            "field_id":9,
            "name": "Physical Injury",
            "option": "Significant/Severe",
            "description": "testt tjtetheht h rerhehrerierherehrer"
        },
        {    
            "field_id":10,
            "name": "Treatment",
            "option": "Immediate and ongoing",
            "description": "fgdgd tjtetheht h gdggdgd"
        },
        {    
            "field_id":9,
            "name": "Case Evaluation",
            "option": "Signed",
            "description": "fgdgd tjtetheht h gdggdgd"
        }
    ]
}

//  get_evaluation
let optndata = {
    "option_ids": [17, 19]
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
    "email": "john@example.com",
    "phone": "+1234567890",
    "generated_outcome":1,
    "updated_out_description":"Checking updated_out_description!",
    "selected_options": [1, 3],
    "updated_description": {
      1: "Updated description for option 1",
      3: "Updated description for option 3"
    },

    "client_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "field_options": [
        {
            field_id : 2,
            name: "Physical Injury",
            option: "Significant/Severe",
            description : "eryeuyrgeuhfbhdhf"
        },
        {
            field_id : 3,
            name: "Treatment",
            option: "Immediate and ongoing",
            description : "eryeuyrgeuhfbhdhf"
        },
        {
            field_id : 5,
            name: "Case Evaluation",
            option: "Signed",
            description : "eryeuyrgeuhfbhdhf"
        },
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


