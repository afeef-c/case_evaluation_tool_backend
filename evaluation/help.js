//by client(admin)
//Add case evaluation form fields
let fieldsData = {
    userId: 1,
    field_options: [
        {
            name: "Physical Injury",
            options: [
                {
                    name: "Significant/Severe",
                    description: "testt tjtetheht h rerhehrerierherehrer"
                },
                {
                    name: "Standard",
                    description: "testt tjtereretheht h fererre"
                }
            ]
        },
        {
            name: "Treatment",
            options: [
                {
                    name: "Immediate and ongoing",
                    description: "fgdgd tjtetheht h gdggdgd"
                },
                {
                    name: "Immediate only, but willing to treat",
                    description: "wewewew wewewe ewewh fererre"
                }
            ]
        }
    ],
    case_evaluation_options: [
        {
            name: "Signed",
            description: "fgdgd tjtetheht h gdggdgd"
        },
        {
            name: "Declined",
            description: "wewewew wewewe ewewh fererre"
        }
    ]
}


//Add case evaluation rules
let rulesData = {
    userId : 1,
    field_options: [
        {
            name: "Physical Injury",
            options: ["Significant/Severe", "Standard"]
        },
        {
            name: "Treatment",
            options: ["Immediate and ongoing"]
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

