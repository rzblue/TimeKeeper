```mermaid
erDiagram
    USER ||--o{ TIME_SESSION : places
    USER {
        int id PK
        string name
        string id_string
    }
    TIME_SESSION {
        int id PK
        int user_id FK
        start_time datetime
        end_time datetime
        total_time datetime
    }
 ```