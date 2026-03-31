"""
测试脚本 - 测试 Company 平台 API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import requests
import json
import tempfile

BASE_URL = "http://localhost:8000"


class TestCompanyAPI:
    
    def __init__(self):
        self.token = None
        self.api_key = None
        self.test_file_id = None
    
    def test_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 Company 平台 API 测试")
        print("=" * 60)
        
        tests = [
            ("健康检查", self.test_health),
            ("用户注册", self.test_register),
            ("用户登录", self.test_login),
            ("获取用户信息", self.test_get_me),
            ("生成 API Key", self.test_generate_api_key),
            ("文件上传（JWT）", self.test_upload_file),
            ("文件列表", self.test_list_files),
            ("文件下载", self.test_download_file),
            ("添加评论", self.test_add_comment),
            ("API Key 文件上传", self.test_upload_by_api_key),
            ("公开文件列表", self.test_public_files),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                test_func()
                print(f"  ✅ {name}")
                passed += 1
            except Exception as e:
                print(f"  ❌ {name}: {e}")
                failed += 1
        
        print()
        print("=" * 60)
        print(f"结果: {passed} passed, {failed} failed")
        print("=" * 60)
        
        return failed == 0
    
    def test_health(self):
        """测试健康检查"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_register(self):
        """测试用户注册"""
        response = requests.post(
            f"{BASE_URL}/api/users/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "test123"
            }
        )
        # 可能已经存在
        assert response.status_code in [200, 400]
    
    def test_login(self):
        """测试用户登录"""
        response = requests.post(
            f"{BASE_URL}/api/users/login",
            data={"username": "testuser", "password": "test123"}
        )
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        assert self.token
    
    def test_get_me(self):
        """测试获取用户信息"""
        response = requests.get(
            f"{BASE_URL}/api/users/me",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
    
    def test_generate_api_key(self):
        """测试生成 API Key"""
        response = requests.post(
            f"{BASE_URL}/api/users/me/api-key",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        self.api_key = response.json()["api_key"]
        assert self.api_key.startswith("cp_")
    
    def test_upload_file(self):
        """测试文件上传"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content for api")
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/api/files/upload",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files={"file": ("test_upload.txt", f)},
                    data={"description": "测试文件", "tags": "test,api"}
                )
            
            assert response.status_code == 200
            self.test_file_id = response.json()["id"]
        finally:
            os.unlink(temp_file)
    
    def test_list_files(self):
        """测试文件列表"""
        response = requests.get(
            f"{BASE_URL}/api/files",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) > 0
    
    def test_download_file(self):
        """测试文件下载"""
        if not self.test_file_id:
            return
        
        response = requests.get(
            f"{BASE_URL}/api/files/{self.test_file_id}/download",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
    
    def test_add_comment(self):
        """测试添加评论"""
        if not self.test_file_id:
            return
        
        response = requests.post(
            f"{BASE_URL}/api/comments",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"file_id": self.test_file_id, "content": "测试评论"}
        )
        assert response.status_code == 200
    
    def test_upload_by_api_key(self):
        """测试 API Key 上传"""
        if not self.api_key:
            return
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("api key upload test")
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/api/files/upload-by-api-key",
                    headers={"X-API-Key": self.api_key},
                    files={"file": ("api_key_test.txt", f)},
                    data={"description": "API Key 测试", "tags": "test,api-key"}
                )
            
            assert response.status_code == 200
        finally:
            os.unlink(temp_file)
    
    def test_public_files(self):
        """测试公开文件列表"""
        response = requests.get(f"{BASE_URL}/api/files/public")
        assert response.status_code == 200


if __name__ == "__main__":
    tester = TestCompanyAPI()
    success = tester.test_all()
    sys.exit(0 if success else 1)
