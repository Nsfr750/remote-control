"""
File transfer protocol for remote control application.
Handles file and directory operations between client and server.
"""
import os
import io
import json
import shutil
import hashlib
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple, Union

class FileTransfer:
    """Handles file transfer operations between client and server."""
    
    CHUNK_SIZE = 65536  # 64KB chunks for file transfer
    
    @staticmethod
    def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
        """Calculate the hash of a file.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use (default: sha256)
            
        Returns:
            Hex digest of the file
        """
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(FileTransfer.CHUNK_SIZE), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> Dict:
        """Get file/directory information.
        
        Args:
            file_path: Path to the file or directory
            
        Returns:
            Dictionary containing file information
        """
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'name': path.name,
            'path': str(path.absolute()),
            'is_dir': path.is_dir(),
            'size': stat.st_size if path.is_file() else 0,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'permissions': oct(stat.st_mode)[-3:],
            'hash': FileTransfer.calculate_file_hash(path) if path.is_file() else ''
        }
    
    @staticmethod
    def list_directory(directory: Union[str, Path]) -> List[Dict]:
        """List contents of a directory.
        
        Args:
            directory: Path to the directory
            
        Returns:
            List of file/directory information dictionaries
        """
        path = Path(directory)
        if not path.is_dir():
            raise NotADirectoryError(f"{directory} is not a directory")
            
        return [FileTransfer.get_file_info(item) for item in path.iterdir()]
    
    @staticmethod
    def read_file_chunks(file_path: Union[str, Path]) -> bytes:
        """Read a file in chunks.
        
        Args:
            file_path: Path to the file
            
        Yields:
            File chunks as bytes
        """
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(FileTransfer.CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk
    
    @staticmethod
    def write_file_chunks(file_path: Union[str, Path], chunks: BinaryIO) -> str:
        """Write file chunks to disk.
        
        Args:
            file_path: Destination path
            chunks: BinaryIO object containing file chunks
            
        Returns:
            SHA-256 hash of the written file
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        hash_func = hashlib.sha256()
        
        with open(path, 'wb') as f:
            while True:
                chunk = chunks.read(FileTransfer.CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def create_directory(directory: Union[str, Path]) -> None:
        """Create a directory.
        
        Args:
            directory: Path to the directory to create
        """
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def delete_path(path: Union[str, Path]) -> None:
        """Delete a file or directory.
        
        Args:
            path: Path to the file or directory to delete
        """
        path = Path(path)
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    
    @staticmethod
    def move_path(src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Move/rename a file or directory.
        
        Args:
            src: Source path
            dst: Destination path
        """
        shutil.move(str(src), str(dst))
    
    @staticmethod
    def copy_path(src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Copy a file or directory.
        
        Args:
            src: Source path
            dst: Destination path
        """
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)
    
    @staticmethod
    def compress_directory(directory: Union[str, Path], output_path: Union[str, Path]) -> None:
        """Compress a directory into a zip file.
        
        Args:
            directory: Directory to compress
            output_path: Path to the output zip file
        """
        shutil.make_archive(str(Path(output_path).with_suffix('')), 'zip', directory)
    
    @staticmethod
    def extract_archive(archive_path: Union[str, Path], extract_to: Union[str, Path]) -> None:
        """Extract an archive file.
        
        Args:
            archive_path: Path to the archive file
            extract_to: Directory to extract to
        """
        shutil.unpack_archive(archive_path, extract_to)
    
    @classmethod
    def serialize_file_list(cls, file_list: List[Dict]) -> bytes:
        """Serialize a list of file information dictionaries.
        
        Args:
            file_list: List of file information dictionaries
            
        Returns:
            Serialized bytes
        """
        return json.dumps(file_list).encode('utf-8')
    
    @classmethod
    def deserialize_file_list(cls, data: bytes) -> List[Dict]:
        """Deserialize a list of file information dictionaries.
        
        Args:
            data: Serialized file list data
            
        Returns:
            List of file information dictionaries
        """
        return json.loads(data.decode('utf-8'))

# File transfer protocol messages
class FileTransferMessage:
    """File transfer protocol message format."""
    
    class Type:
        LIST_DIR = 'list_dir'
        GET_FILE = 'get_file'
        PUT_FILE = 'put_file'
        DELETE = 'delete'
        MOVE = 'move'
        COPY = 'copy'
        MKDIR = 'mkdir'
        STAT = 'stat'
        ERROR = 'error'
    
    @staticmethod
    def create_list_dir(path: str) -> Dict:
        """Create a list directory message."""
        return {'type': FileTransferMessage.Type.LIST_DIR, 'path': path}
    
    @staticmethod
    def create_get_file(path: str, offset: int = 0) -> Dict:
        """Create a get file message."""
        return {'type': FileTransferMessage.Type.GET_FILE, 'path': path, 'offset': offset}
    
    @staticmethod
    def create_put_file(path: str, size: int, mode: str = 'wb') -> Dict:
        """Create a put file message."""
        return {'type': FileTransferMessage.Type.PUT_FILE, 'path': path, 'size': size, 'mode': mode}
    
    @staticmethod
    def create_delete(path: str) -> Dict:
        """Create a delete message."""
        return {'type': FileTransferMessage.Type.DELETE, 'path': path}
    
    @staticmethod
    def create_move(src: str, dst: str) -> Dict:
        """Create a move/rename message."""
        return {'type': FileTransferMessage.Type.MOVE, 'src': src, 'dst': dst}
    
    @staticmethod
    def create_copy(src: str, dst: str) -> Dict:
        """Create a copy message."""
        return {'type': FileTransferMessage.Type.COPY, 'src': src, 'dst': dst}
    
    @staticmethod
    def create_mkdir(path: str) -> Dict:
        """Create a make directory message."""
        return {'type': FileTransferMessage.Type.MKDIR, 'path': path}
    
    @staticmethod
    def create_stat(path: str) -> Dict:
        """Create a file stat message."""
        return {'type': FileTransferMessage.Type.STAT, 'path': path}
    
    @staticmethod
    def create_error(message: str, code: int = 0) -> Dict:
        """Create an error message."""
        return {'type': FileTransferMessage.Type.ERROR, 'message': message, 'code': code}
    
    @staticmethod
    def serialize(message: Dict) -> bytes:
        """Serialize a message to bytes."""
        return json.dumps(message).encode('utf-8')
    
    @staticmethod
    def deserialize(data: bytes) -> Dict:
        """Deserialize a message from bytes."""
        return json.loads(data.decode('utf-8'))
