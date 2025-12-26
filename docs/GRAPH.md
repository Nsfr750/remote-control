# Project Graph

## Project Structure Diagram

```mermaid
graph TD
    A[Project Structure] --> B[remote_control/]
    B --> C[client/]
    B --> D[server/]
    B --> E[common/]
    B --> F[requirements.txt]
    B --> G[README.md]
    C --> H[__init__.py]
    C --> I[client.py]
    C --> J[gui.py]
    D --> K[__init__.py]
    D --> L[server.py]
    D --> M[remote_control.py]
    E --> N[__init__.py]
    E --> O[protocol.py]
    E --> P[security.py]
    E --> Q[file_transfer.py]
```

## Architecture Flow

```mermaid
graph TD
    A[Client Application] --> B[Network Layer]
    B --> C[Server Application]
    C --> D[Platform Layer]
    D --> E[Windows API]
    D --> F[Linux API]
    C --> G[File System]
    C --> H[Screen Capture]
    C --> I[Input Control]
```

## Communication Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant P as Platform
    
    C->>S: Connect Request
    S->>C: Authentication Challenge
    C->>S: Credentials
    S->>C: Session Token
    
    loop Remote Control Session
        C->>S: Input Events
        S->>P: Process Input
        P->>S: Input Result
        S->>C: Confirmation
        
        C->>S: Screen Request
        S->>P: Capture Screen
        P->>S: Screen Data
        S->>C: Screen Image
    end
    
    C->>S: Disconnect
    S->>C: Close Connection
```

## Component Dependencies

```mermaid
graph LR
    subgraph "Client Components"
        A1[GUI Layer] --> A2[Network Layer]
        A2 --> A3[Protocol Layer]
        A3 --> A4[Security Layer]
    end
    
    subgraph "Server Components"
        B1[Network Layer] --> B2[Authentication]
        B2 --> B3[Session Manager]
        B1 --> B4[Platform Layer]
        B4 --> B5[Screen Capture]
        B4 --> B6[Input Control]
    end
    
    subgraph "Shared Components"
        C1[Protocol] --> C2[Security]
        C2 --> C3[File Transfer]
    end
```

## Data Flow Architecture

```mermaid
graph TD
    A[User Input] --> B[Client GUI]
    B --> C[Message Serializer]
    C --> D[Network Socket]
    D --> E[Server Socket]
    E --> F[Message Deserializer]
    F --> G[Authentication]
    G --> H[Platform Handler]
    H --> I[System API]
    I --> J[Screen Capture]
    J --> K[Image Processing]
    K --> L[Network Response]
    L --> M[Client Display]
```

## Platform Abstraction

```mermaid
graph TD
    A[Application Layer] --> B[Platform Interface]
    B --> C[Windows Implementation]
    B --> D[Linux Implementation]
    
    C --> E[Windows API]
    C --> F[GDI Screen Capture]
    C --> G[SendInput API]
    
    D --> H[X11 Display]
    D --> I[Import/Scrot Tools]
    D --> J[PyAutoGUI Library]
```

## Security Architecture

```mermaid
graph TD
    A[Client Request] --> B[Encryption Layer]
    B --> C[AES-256 Encryption]
    C --> D[Network Transmission]
    D --> E[Server Decryption]
    E --> F[Authentication Module]
    F --> G[PBKDF2 Password Hashing]
    G --> H[Session Management]
    H --> I[Authorization Check]
    I --> J[Resource Access]
```

## File Transfer Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant FS as File System
    
    Note over C,S: Upload Operation
    C->>S: FILE_TRANSFER Request
    S->>S: Validate Path
    S->>FS: Write File
    FS->>S: Write Result
    S->>C: Transfer Status
    
    Note over C,S: Download Operation
    C->>S: FILE_TRANSFER Request
    S->>S: Validate Path
    S->>FS: Read File
    FS->>S: File Data
    S->>C: Transfer Response
```

## Performance Optimization Flow

```mermaid
graph TD
    A[Screen Capture] --> B[Image Compression]
    B --> C[JPEG Optimization]
    C --> D[Network Transfer]
    D --> E[Client Display]
    
    F[Differential Capture] --> G[Change Detection]
    G --> H[Partial Updates]
    H --> D
    
    I[Connection Pooling] --> J[Resource Management]
    J --> D
    
    K[Rate Limiting] --> L[Abuse Prevention]
    L --> D
```

## Module Interaction Graph

```mermaid
graph TD
    subgraph "Client Module"
        A1[client.py] --> A2[gui/]
        A2 --> A3[main_window.py]
        A2 --> A4[login_dialog.py]
        A2 --> A5[file_browser.py]
    end
    
    subgraph "Server Module"
        B1[server.py] --> B2[platform/]
        B2 --> B3[windows/]
        B2 --> B4[linux/]
        B3 --> B5[screen.py]
        B3 --> B6[input.py]
        B4 --> B7[screen.py]
        B4 --> B8[input.py]
    end
    
    subgraph "Common Module"
        C1[protocol.py] --> C2[message types]
        C1 --> C3[serialization]
        C4[security.py] --> C5[encryption]
        C4 --> C6[authentication]
        C7[file_transfer.py] --> C8[upload/download]
    end
```

## Build System Graph

```mermaid
graph TD
    A[Source Code] --> B[Build Scripts]
    B --> C[Nuitka Compilation]
    C --> D[Static Analysis]
    D --> E[Code Signing]
    E --> F[Distribution]
    
    G[Dependencies] --> H[virtualenv]
    H --> I[requirements.txt]
    I --> J[pip install]
    J --> A
```

## Deployment Architecture

```mermaid
graph TD
    A[Development] --> B[Testing]
    B --> C[Build Process]
    C --> D[Package Creation]
    D --> E[Distribution]
    
    F[Windows Deployment] --> G[EXE Installer]
    F --> H[Code Signing]
    F --> I[Windows Defender Config]
    
    J[Linux Deployment] --> K[Python Package]
    J --> L[System Dependencies]
    J --> M[X11 Configuration]
```

---

**Last Updated**: December 26, 2025  
**Version**: 1.0.0  
**License**: GPLv3
