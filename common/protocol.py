"""
Remote Control Protocol

Defines the communication protocol between client and server.
"""
import json
import struct
from enum import Enum, auto
from typing import Any, Dict, Tuple, Union

class MessageType(Enum):
    """Message types for client-server communication."""
    AUTH = 0
    AUTH_RESPONSE = 1
    MOUSE_MOVE = 2
    MOUSE_CLICK = 3
    KEY_EVENT = 4
    SCREENSHOT = 5
    FILE_TRANSFER = 6
    CLIPBOARD_UPDATE = 7
    SYSTEM_COMMAND = 8
    SUCCESS = 9
    ERROR = 10
    INFO = 11
    DISCONNECT = 12
    PING = 13        # Keep-alive ping
    PONG = 14        # Keep-alive pong response

class Message:
    """Message class for client-server communication."""
    HEADER_SIZE = 8  # 4 bytes for message type, 4 bytes for data length
    
    def __init__(self, msg_type: MessageType, data: bytes = b''):
        self.type = msg_type
        self.data = data
    
    def serialize(self) -> bytes:
        """Serialize message to bytes for transmission."""
        msg_type = self.type.value.to_bytes(4, byteorder='big')
        data_len = len(self.data).to_bytes(4, byteorder='big')
        return msg_type + data_len + self.data
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'Message':
        """Deserialize bytes to Message object."""
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Invalid message format: message too short")
        
        msg_type = MessageType(int.from_bytes(data[:4], byteorder='big'))
        data_len = int.from_bytes(data[4:8], byteorder='big')
        
        if len(data) < cls.HEADER_SIZE + data_len:
            raise ValueError("Incomplete message: data length mismatch")
        
        msg_data = data[8:8+data_len]
        return cls(msg_type, msg_data)

class AuthMessage:
    """Authentication message format."""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
    
    def to_bytes(self) -> bytes:
        """Convert to bytes for transmission."""
        return json.dumps({
            'username': self.username,
            'password': self.password
        }).encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'AuthMessage':
        """Create from received bytes."""
        data_dict = json.loads(data.decode('utf-8'))
        return cls(data_dict['username'], data_dict['password'])

class MouseEvent:
    """Mouse event message format."""
    def __init__(self, x: int, y: int, button: int = 0, pressed: bool = False):
        self.x = x
        self.y = y
        self.button = button  # 0=left, 1=middle, 2=right
        self.pressed = pressed
    
    def to_bytes(self) -> bytes:
        """Convert to bytes for transmission."""
        return struct.pack('!hhBB', self.x, self.y, self.button, int(self.pressed))
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'MouseEvent':
        """Create from received bytes."""
        x, y, button, pressed = struct.unpack('!hhBB', data)
        return cls(x, y, button, bool(pressed))

class KeyEvent:
    """Keyboard event message format."""
    def __init__(self, key: str, pressed: bool):
        self.key = key
        self.pressed = pressed
    
    def to_bytes(self) -> bytes:
        """Convert to bytes for transmission."""
        return json.dumps({
            'key': self.key,
            'pressed': self.pressed
        }).encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'KeyEvent':
        """Create from received bytes."""
        data_dict = json.loads(data.decode('utf-8'))
        return cls(data_dict['key'], data_dict['pressed'])
