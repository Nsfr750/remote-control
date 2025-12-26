# API Documentation

## Overview

The Remote Control application provides a comprehensive API for client-server communication, file operations, and platform-specific functionality.

## Table of Contents
1. [Message Protocol](#message-protocol)
2. [Client API](#client-api)
3. [Server API](#server-api)
4. [File Transfer API](#file-transfer-api)
5. [Platform APIs](#platform-apis)
6. [Examples](#examples)

## Message Protocol

### Message Types
This document describes the binary protocol and message formats used by the Remote Control application for communication between clients and servers.

## Protocol Overview

Communication between client and server uses a binary protocol with the following characteristics:
- **Binary protocol** for efficiency
- **Message-based** communication
- **Synchronous request-response** pattern
- **Keepalive** mechanism for connection monitoring

## Message Types

The following message types are defined in the protocol:

| Type | Value | Description |
|------|-------|-------------|
| AUTH | 0 | Authentication request |
| AUTH_RESPONSE | 1 | Authentication response |
| MOUSE_MOVE | 2 | Mouse movement event |
| MOUSE_CLICK | 3 | Mouse click event |
| KEY_EVENT | 4 | Keyboard event |
| SCREENSHOT | 5 | Screenshot data |
| FILE_TRANSFER | 6 | File transfer operations |
| CLIPBOARD_UPDATE | 7 | Clipboard content update |
| SYSTEM_COMMAND | 8 | System command execution |
| ERROR | 9 | Error response |
| INFO | 10 | System information |
| DISCONNECT | 11 | Graceful disconnection |
| PING | 12 | Keepalive ping |
| PONG | 13 | Keepalive pong response |

## Authentication

### Authentication Flow
1. Client connects to the server
2. Client sends `AUTH` message with credentials
3. Server validates credentials and responds with `AUTH_RESPONSE`
4. If successful, client can send other message types

Note: starting from version 1.0.1, authentication failures are returned as `AUTH_RESPONSE` with `success: false` (not as `ERROR`).

### Authentication Request
```json
{
  "username": "user123",
  "password": "hashed_password"
}
```

### Authentication Response (Success)
```json
{
  "success": true,
  "message": "Authentication successful"
}
```

### Authentication Response (Failure)
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

## Message Format

All messages follow the same binary format:

```
+----------------+----------------+------------------+
|  Message Type  |  Data Length   |      Data        |
|    (4 bytes)   |   (4 bytes)    |   (N bytes)      |
+----------------+----------------+------------------+
```

- **Message Type**: 4-byte big-endian integer representing the message type
- **Data Length**: 4-byte big-endian integer representing the length of the data payload
- **Data**: The actual message payload (format depends on message type)

## Client-Server API

### Mouse Movement
- **Type**: `MOUSE_MOVE` (2)
- **Data Format**: Binary (x: int16, y: int16)

### Mouse Click
- **Type**: `MOUSE_CLICK` (3)
- **Data Format**: Binary (x: int16, y: int16, button: uint8, pressed: uint8)
  - button: 0=left, 1=middle, 2=right
  - pressed: 0=released, 1=pressed

### Keyboard Event
- **Type**: `KEY_EVENT` (4)
- **Data Format**: JSON

  ```json
  {
    "key": "a",
    "pressed": true
  }
  ```

### Screenshot Request
- **Type**: `SCREENSHOT` (5)
- **Response**: Binary image data (PNG format)

### System Information
- **Type**: `INFO` (10)
- **Response**: JSON with system information

  ```json
  {
    "platform": "Windows-10-10.0.19041-SP0",
    "python_version": "3.9.7",
    "hostname": "DESKTOP-ABC123",
    "cpu_count": 8,
    "system": "Windows",
    "release": "10",
    "machine": "AMD64",
    "processor": "Intel64 Family 6 Model 158 Stepping 10, GenuineIntel"
  }
  ```

## Error Handling

### Error Response
- **Type**: `ERROR` (9)
- **Data Format**: UTF-8 encoded error message string

## Debugging

Log files are saved under the project `logs/` folder:
- `logs/server.log`
- `logs/client_debug.log`

## File Transfer

### File Transfer Message
- **Type**: `FILE_TRANSFER` (6)
- **Data Format**: JSON

  ```json
  {
    "operation": "upload|download|delete|list",
    "path": "/path/to/file",
    "data": "base64_encoded_data",  // For uploads only
    "overwrite": true|false,       // For uploads only
    "recursive": true|false        // For list/delete operations
  }
  ```

## Keepalive

### Ping
- **Type**: `PING` (12)
- **Data**: Empty

### Pong
- **Type**: `PONG` (13)
- **Data**: Empty

Clients should respond to PING messages with PONG. If no messages are received for a period (recommended: 30 seconds), the connection may be considered dead.