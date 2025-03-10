
---

## **Markdown Format**

### **User Model**
| Field            | Data Type | Description                                    |
|------------------|-----------|------------------------------------------------|
| id               | UUID      | Unique identifier for each user                |
| full_name        | String    | User's complete name                           |
| email            | String    | Unique email address                           |
| password         | String    | Bcrypt-encrypted password                      |
| profile_picture  | String    | URL to the user's profile image                |
| bio              | String    | Brief biography                                |
| location         | String    | User's location                                |
| role             | Enum      | Role of the user: Entrepreneur or Investor     |
| is_verified      | Boolean   | Indicates if the account is verified           |
| is_active        | Boolean   | Indicates if the account is active             |
| created_at       | DateTime  | Timestamp of account creation                  |
| updated_at       | DateTime  | Timestamp for last update                      |

---

### **Entrepreneur Model**
| Field                 | Data Type         | Description                                                        |
|-----------------------|-------------------|--------------------------------------------------------------------|
| id                    | UUID              | Unique identifier for the entrepreneur profile                     |
| user_id               | UUID              | Reference to the associated User record                            |
| education_background  | List of Dict      | List of degrees, institutions, years, and fields of study            |
| skills                | List of Strings   | List of entrepreneur's skills                                        |
| area_of_interest      | List of Strings   | Industries or domains of interest                                    |
| work_experience       | List of Dict      | Previous work experience details                                     |
| previous_startups     | List of Dict      | List of previous startups and roles                                  |
| certifications        | List of Strings   | List of professional certifications (optional)                       |
| portfolio_links       | List of Strings   | URLs to entrepreneur's portfolios (e.g., LinkedIn, GitHub)             |
| created_at            | DateTime          | Timestamp of profile creation                                        |
| updated_at            | DateTime          | Timestamp for last update                                            |

---

### **Investor Model**
| Field                  | Data Type         | Description                                               |
|------------------------|-------------------|-----------------------------------------------------------|
| id                     | UUID              | Unique identifier for the investor profile                |
| user_id                | UUID              | Reference to the associated User record                   |
| investor_type          | Enum              | Investor type: Angel, VC, Corporate, Government            |
| funds_available        | Float             | Investment capital available                              |
| investment_interests   | List of Strings   | Industries or sectors of interest                         |
| previous_investments   | List of Dict      | List of past investments                                  |
| preferred_funding_stage| Enum              | Preferred investment stage                                |
| created_at             | DateTime          | Timestamp of profile creation                             |
| updated_at             | DateTime          | Timestamp for last update                                 |

---

### **Startup Model**
| Field             | Data Type         | Description                                                     |
|-------------------|-------------------|-----------------------------------------------------------------|
| id                | UUID              | Unique identifier for the startup                               |
| startup_name      | String            | Name of the startup                                             |
| description       | Text              | Detailed business overview                                      |
| industry          | String            | Market sector of the startup                                    |
| website           | String            | Startup's website URL                                             |
| founders          | List of UUIDs     | List of entrepreneur user IDs                                   |
| market_size       | String            | Estimated potential market size                                  |
| previous_fundings | List of Dict      | List of past funding rounds; each record includes:              |
|                   |                   | - startup_name, stage, amount, date                             |
|                   |                   | - investors: List of investor IDs (if internal) or external names |
| equity_split      | List of Dict      | Equity distribution; each record includes:                      |
|                   |                   | - For founders: founder_id, name, equity_percentage             |
|                   |                   | - For investors: investor_id, name, equity_percentage            |
| created_at        | DateTime          | Timestamp of startup creation                                   |
| updated_at        | DateTime          | Timestamp for last update                                         |

---

### **Follow Model**
| Field        | Data Type | Description                                |
|--------------|-----------|--------------------------------------------|
| follower_id  | UUID      | User ID of the follower                    |
| following_id | UUID      | User ID of the followed user               |
| created_at   | DateTime  | Timestamp when the follow occurred         |

---

### **Post Model**
| Field         | Data Type | Description                                  |
|---------------|-----------|----------------------------------------------|
| id            | UUID      | Unique identifier for the post               |
| user_id       | UUID      | User ID of the post creator                  |
| content       | Text      | Text content of the post                     |
| image_url     | String    | Optional image URL associated with the post  |
| created_at    | DateTime  | Timestamp when the post was created          |
| updated_at    | DateTime  | Timestamp for last update                    |

---

### **Chat Model**
| Field         | Data Type | Description                                   |
|---------------|-----------|-----------------------------------------------|
| id            | UUID      | Unique identifier for the message             |
| sender_id     | UUID      | User ID of the sender                         |
| receiver_id   | UUID      | User ID of the receiver                       |
| message_body  | Text      | Content of the message                         |
| timestamp     | DateTime  | Timestamp when the message was sent            |
| is_read       | Boolean   | Indicates if the message has been read         |

---

### **Pitch Model**
| Field         | Data Type | Description                                       |
|---------------|-----------|---------------------------------------------------|
| id            | UUID      | Unique identifier for the pitch                    |
| startup_id    | UUID      | Foreign key referencing the Startup model          |
| title         | String    | Title of the pitch                                 |
| description   | Text      | Detailed explanation of the pitch                |
| market_type   | String    | Type of market targeted                            |
| market_size   | String    | Estimated market size                              |
| revenue_model | Text      | Revenue generation model                           |
| created_at    | DateTime  | Timestamp of pitch submission                      |
| updated_at    | DateTime  | Timestamp for last update                          |

---
