
---

### **User Model**
| Field             | Data Type         | Description                                                   |
|-------------------|-------------------|---------------------------------------------------------------|
| id                | UUID              | Unique identifier for each user                               |
| full_name         | String            | User's complete name                                          |
| email             | String            | Unique email address                                          |
| password          | String            | Bcrypt-encrypted password                                     |
| profile_picture   | String            | URL to the user's profile image                               |
| bio               | String            | Brief biography                                               |
| location          | String            | User's location                                               |
| role              | Enum              | Role of the user: Entrepreneur or Investor                    |
| followers         | List of UUIDs     | List of user IDs who follow this user                         |
| following         | List of UUIDs     | List of user IDs that this user follows                        |
| posts             | List of UUIDs     | List of post IDs created by the user                          |
| current_startup   | Optional[UUID]    | ID of the startup the user is currently active in (if applicable)|
| is_verified       | Boolean           | Indicates if the account is verified                          |
| is_active         | Boolean           | Indicates if the account is active                            |
| created_at        | DateTime          | Timestamp of account creation                                 |
| updated_at        | DateTime          | Timestamp for last update                                     |

---

### **Entrepreneur Model**
| Field                | Data Type         | Description                                                                |
|----------------------|-------------------|----------------------------------------------------------------------------|
| id                   | UUID              | Unique identifier for the entrepreneur profile                             |
| user_id              | UUID              | Reference to the associated User record                                    |
| education_background | List of Dict      | List of degrees, institutions, years, and fields of study                  |
| skills               | List of Strings   | List of entrepreneur's skills                                              |
| area_of_interest     | List of Strings   | Industries or domains of interest                                          |
| work_experience      | List of Dict      | Previous work experience details (company_name, role, duration, description) |
| previous_startups    | List of Dict      | List of previous startups and roles (startup_id, startup_name, role, duration)|
| certifications       | List of Strings   | Professional certifications (optional)                                   |
| portfolio_links      | List of Strings   | URLs to portfolios (e.g., LinkedIn, GitHub)                                  |
| created_at           | DateTime          | Timestamp of profile creation                                              |
| updated_at           | DateTime          | Timestamp for last update                                                  |

---

### **Investor Model**
| Field                   | Data Type         | Description                                                        |
|-------------------------|-------------------|--------------------------------------------------------------------|
| id                      | UUID              | Unique identifier for the investor profile                         |
| user_id                 | UUID              | Reference to the associated User record                            |
| investor_type           | Enum              | Type of investor: Angel, VC, Corporate, Government                   |
| funds_available         | Float             | Investment capital available                                       |
| investment_interests    | List of Strings   | Industries or sectors of interest                                  |
| previous_investments    | List of Dict      | List of past investments (startup_id, startup_name, amount, date)      |
| preferred_funding_stage | Enum              | Preferred investment stage (e.g., Seed, Series A)                    |
| created_at              | DateTime          | Timestamp of profile creation                                      |
| updated_at              | DateTime          | Timestamp for last update                                          |

---

### **Startup Model**
| Field              | Data Type         | Description                                                                                           |
|--------------------|-------------------|-------------------------------------------------------------------------------------------------------|
| id                 | UUID              | Unique identifier for the startup                                                                     |
| startup_name       | String            | Name of the startup                                                                                   |
| description        | Text              | Detailed overview of what the startup does (explains what the startup actually does)                   |
| industry           | String            | Market sector of the startup                                                                          |
| website            | String            | Startup's website URL                                                                                 |
| logo_url           | Optional[String]  | URL to the startup's logo                                                                              |
| founders           | List of UUIDs     | List of entrepreneur user IDs (founders)                                                              |
| market_size        | String            | Approximate potential market size                                                                     |
| revenue_model      | Optional[String]  | Revenue generation model (optional; updated when pitch is added)                                      |
| contact_details    | Optional[String]  | Contact details for further inquiries (optional; used to redirect to founders’ chat)                   |
| previous_fundings  | Optional[List of Dict] | List of past funding rounds; each record includes: <br> - startup_name, stage, amount, date <br> - investors: List of investor IDs (internal) or names (external) |
| equity_split       | Optional[List of Dict] | Equity distribution; each record includes: <br> - For founders: founder_id, name, equity_percentage <br> - For investors: investor_id, name, equity_percentage <br> - For ESOP: name, equity_percentage |
| created_at         | DateTime          | Timestamp of startup creation                                                                         |
| updated_at         | DateTime          | Timestamp for last update                                                                             |

---

### **Chat Model**
| Field        | Data Type         | Description                                               |
|--------------|-------------------|-----------------------------------------------------------|
| id           | UUID              | Unique identifier for the chat message                     |
| sender_id    | UUID              | User ID of the sender                                       |
| receiver_id  | UUID              | User ID of the receiver                                     |
| message_body | Text              | Content of the message                                       |
| timestamp    | DateTime          | Timestamp when the message was sent                          |
| is_read      | Boolean           | Indicates if the message has been read                       |

---

### **Post Model**
| Field         | Data Type             | Description                                                                                  |
|---------------|-----------------------|----------------------------------------------------------------------------------------------|
| id            | UUID                  | Unique identifier for the post                                                                |
| user_id       | UUID                  | User ID of the post creator                                                                   |
| content       | Text                  | Text content of the post                                                                      |
| image_url     | String                | Optional image URL associated with the post                                                   |
| likes         | List of UUIDs         | List of user IDs who liked the post                                                           |
| comments      | List of UUIDs         | List of comment IDs associated with the post                                                  |
| created_at    | DateTime              | Timestamp when the post was created                                                           |
| updated_at    | DateTime              | Timestamp for last update                                                                      |

---

### **Comment Model**
| Field         | Data Type         | Description                                                                                  |
|---------------|-------------------|----------------------------------------------------------------------------------------------|
| id            | UUID              | Unique identifier for the comment                                                            |
| post_id       | UUID              | Reference to the associated Post                                                             |
| user_id       | UUID              | User ID of the commenter                                                                       |
| content       | Text              | Text content of the comment                                                                    |
| created_at    | DateTime          | Timestamp when the comment was created                                                         |
| updated_at    | DateTime          | Timestamp for last update                                                                      |

---
