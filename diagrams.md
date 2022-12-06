## DB Schema
```mermaid
erDiagram
    USER ||--o{ TIME_SESSION : has
    USER {
        int id PK
        string name
        string id_string
    }
    TIME_SESSION {
        int id PK
        int user_id FK
        string start_time
        string start_time
    }
 ```
# Classes
```mermaid
classDiagram
    class User {
        name: string
        id_string: string
    }
    class TimeSession {
        user_id: int
        start_time: datetime
        end_time: datetime
        total_time: timedelta
    }
```
## UI flow key
```mermaid
flowchart TD
    Z[Display]
    ZZ{{Decision}}
    ZZZ[/User action/]
    ZZZZ([Code action])
```
## Sign-In/Out UI Flow
```mermaid
flowchart TD
    AA[Main Page] -->A
    A[/Sign in button clicked/] --> B{{User ID string valid?}}
    B -->|YES| C{{User signed in?}}
    B -->|NO| ER
    C ---> |YES|D
    D([End session, save current time to end_time]) --> AA
    C ---> |NO|E
    E([Start session, save current time to start_time]) --> AA
    
    ER[Error! Warn user then redirect back.] --> AA
```
