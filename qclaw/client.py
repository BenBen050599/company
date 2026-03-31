"""
QClaw API 客户端
用于 QClaw 与 Company 平台交互
"""
import requests
from typing import List, Dict, Optional
import os


class CompanyClient:
    """Company 平台 API 客户端"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        初始化客户端
        
        Args:
            base_url: 平台地址，如 "http://localhost:8000"
            api_key: 用户的 API Key
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}
    
    def list_files(self) -> List[Dict]:
        """获取文件列表"""
        response = requests.get(f"{self.base_url}/api/files/public")
        response.raise_for_status()
        return response.json()
    
    def get_file(self, file_id: int) -> Dict:
        """获取文件详情"""
        response = requests.get(
            f"{self.base_url}/api/files/{file_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def download_file(self, file_id: int, save_path: str) -> str:
        """
        下载文件到本地
        
        Args:
            file_id: 文件 ID
            save_path: 保存路径
        
        Returns:
            文件路径
        """
        response = requests.get(
            f"{self.base_url}/api/files/{file_id}/download",
            headers=self.headers,
            stream=True
        )
        response.raise_for_status()
        
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return save_path
    
    def upload_file(
        self,
        file_path: str,
        description: str = "",
        tags: str = ""
    ) -> Dict:
        """
        上传文件
        
        Args:
            file_path: 文件路径
            description: 描述
            tags: 标签（逗号分隔）
        
        Returns:
            上传结果
        """
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {"description": description, "tags": tags}
            
            response = requests.post(
                f"{self.base_url}/api/files/upload-by-api-key",
                files=files,
                data=data,
                headers=self.headers
            )
        
        response.raise_for_status()
        return response.json()
    
    def add_comment(self, file_id: int, content: str) -> Dict:
        """
        添加评论
        
        Args:
            file_id: 文件 ID
            content: 评论内容
        
        Returns:
            评论详情
        """
        response = requests.post(
            f"{self.base_url}/api/comments",
            json={"file_id": file_id, "content": content},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_comments(self, file_id: int) -> List[Dict]:
        """获取文件的所有评论"""
        response = requests.get(
            f"{self.base_url}/api/files/{file_id}/comments",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


# ── 便捷函数 ──────────────────────────────────────

def create_client(config_path: str = "config.json") -> CompanyClient:
    """
    从配置文件创建客户端
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        CompanyClient 实例
    """
    import json
    
    with open(config_path) as f:
        config = json.load(f)
    
    return CompanyClient(
        base_url=config.get("base_url", "http://localhost:8000"),
        api_key=config["api_key"]
    )


if __name__ == "__main__":
    # 测试
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python client.py <base_url> <api_key>")
        print("Example: python client.py http://localhost:8000 cp_xxx...")
        sys.exit(1)
    
    client = CompanyClient(sys.argv[1], sys.argv[2])
    
    print("📋 文件列表：")
    files = client.list_files()
    for f in files:
        print(f"  - [{f['id']}] {f['filename']} ({f['file_size']} bytes)")
