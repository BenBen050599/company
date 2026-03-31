import { useState, useEffect } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [apiKey, setApiKey] = useState(localStorage.getItem('apiKey'))
  const [files, setFiles] = useState([])
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [user, setUser] = useState(null)
  const [showRegister, setShowRegister] = useState(false)
  const [users, setUsers] = useState([])
  const [showAdmin, setShowAdmin] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [showComments, setShowComments] = useState(false)

  // 获取公开文件列表
  useEffect(() => {
    fetch(`${API_URL}/api/files/public`)
      .then(res => res.json())
      .then(data => setFiles(data))
      .catch(err => console.error('获取文件失败:', err))
  }, [])

  // 获取用户信息
  useEffect(() => {
    if (token) {
      fetch(`${API_URL}/api/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => setUser(data))
        .catch(() => {
          localStorage.removeItem('token')
          setToken(null)
        })
    }
  }, [token])

  // 登录
  const handleLogin = async (e) => {
    e.preventDefault()
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const res = await fetch(`${API_URL}/api/users/login`, {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    
    if (data.access_token) {
      localStorage.setItem('token', data.access_token)
      setToken(data.access_token)
      setUsername('')
      setPassword('')
    } else {
      alert('登录失败: ' + (data.detail || '未知错误'))
    }
  }

  // 注册
  const handleRegister = async (e) => {
    e.preventDefault()
    const res = await fetch(`${API_URL}/api/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        email,
        full_name: fullName,
        password
      })
    })
    const data = await res.json()
    
    if (data.id) {
      alert('注册成功！请登录')
      setShowRegister(false)
      setUsername('')
      setPassword('')
      setEmail('')
      setFullName('')
    } else {
      alert('注册失败: ' + (data.detail || '未知错误'))
    }
  }

  // 生成 API Key
  const handleGenerateApiKey = async () => {
    const res = await fetch(`${API_URL}/api/users/me/api-key`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    if (data.api_key) {
      setApiKey(data.api_key)
      localStorage.setItem('apiKey', data.api_key)
      alert('API Key: ' + data.api_key)
    }
  }

  // 获取所有用户（管理员）
  const loadUsers = async () => {
    const res = await fetch(`${API_URL}/api/admin/users`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      setUsers(data)
    }
  }

  // 删除用户（管理员）
  const handleDeleteUser = async (userId) => {
    if (!confirm('确定删除此用户？')) return
    
    const res = await fetch(`${API_URL}/api/admin/users/${userId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      alert('用户已删除')
      loadUsers()
    }
  }

  // 上传文件
  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)
    formData.append('description', '网页上传')
    formData.append('tags', 'web')

    const res = await fetch(`${API_URL}/api/files/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    })

    if (res.ok) {
      alert('上传成功！')
      const filesRes = await fetch(`${API_URL}/api/files/public`)
      const filesData = await filesRes.json()
      setFiles(filesData)
    } else {
      alert('上传失败')
    }
  }

  // 下载文件
  const handleDownload = async (fileId, filename) => {
    const res = await fetch(`${API_URL}/api/files/${fileId}/download`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
  }

  // 加载评论
  const loadComments = async (fileId) => {
    const res = await fetch(`${API_URL}/api/files/${fileId}/comments`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      setComments(data)
    }
  }

  // 添加评论
  const handleAddComment = async (e) => {
    e.preventDefault()
    if (!newComment.trim() || !selectedFile) return

    const res = await fetch(`${API_URL}/api/comments`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_id: selectedFile.id,
        content: newComment
      })
    })

    if (res.ok) {
      setNewComment('')
      loadComments(selectedFile.id)
    }
  }

  // 查看文件详情
  const handleViewFile = async (file) => {
    setSelectedFile(file)
    setShowComments(true)
    loadComments(file.id)
  }

  return (
    <div className="container">
      <h1>🏢 Company 团队协作平台</h1>
      
      {/* 使用提示 */}
      <div className="card hint-card">
        <h3>💡 使用提示</h3>
        <p>1. <strong>注册/登录</strong>：点击下方按钮创建账户或登录</p>
        <p>2. <strong>上传文件</strong>：登录后点击"上传文件"按钮</p>
        <p>3. <strong>评论讨论</strong>：点击文件的"评论"按钮进行讨论</p>
        <p>4. <strong>QClaw 集成</strong>：生成 API Key 后，QClaw 可以自动访问和处理文件</p>
      </div>

      {/* 登录/注册区域 */}
      {!token ? (
        <div className="card">
          {showRegister ? (
            <>
              <h2>注册新账户</h2>
              <form onSubmit={handleRegister}>
                <input
                  type="text"
                  placeholder="用户名"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required
                />
                <input
                  type="email"
                  placeholder="邮箱"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />
                <input
                  type="text"
                  placeholder="姓名"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  required
                />
                <input
                  type="password"
                  placeholder="密码"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                />
                <button type="submit">注册</button>
                <button type="button" onClick={() => setShowRegister(false)} className="secondary">
                  返回登录
                </button>
              </form>
            </>
          ) : (
            <>
              <h2>登录</h2>
              <form onSubmit={handleLogin}>
                <input
                  type="text"
                  placeholder="用户名"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required
                />
                <input
                  type="password"
                  placeholder="密码"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                />
                <button type="submit">登录</button>
                <button type="button" onClick={() => setShowRegister(true)} className="secondary">
                  注册新账户
                </button>
              </form>
            </>
          )}
        </div>
      ) : (
        <div className="card">
          <h2>欢迎, {user?.full_name || username}! {user?.is_admin && '👑'}</h2>
          <div className="actions">
            <label className="upload-btn">
              📁 上传文件
              <input type="file" onChange={handleUpload} hidden />
            </label>
            <button onClick={handleGenerateApiKey}>🔑 生成 API Key</button>
            {user?.is_admin && (
              <button onClick={() => {
                setShowAdmin(!showAdmin)
                if (!showAdmin) loadUsers()
              }} className="admin-btn">
                👥 管理用户
              </button>
            )}
            <button onClick={() => {
              localStorage.removeItem('token')
              setToken(null)
              setUser(null)
            }}>登出</button>
          </div>
          {apiKey && (
            <div className="api-key">
              <strong>你的 API Key:</strong>
              <code>{apiKey}</code>
              <small>（用于 QClaw 集成）</small>
            </div>
          )}
        </div>
      )}

      {/* 管理员面板 */}
      {showAdmin && user?.is_admin && (
        <div className="card">
          <h2>👥 用户管理</h2>
          <div className="user-list">
            {users.map(u => (
              <div key={u.id} className="user-item">
                <div>
                  <strong>{u.full_name}</strong> ({u.username})
                  <br />
                  <small>{u.email}</small>
                  {u.is_admin && <span className="badge">管理员</span>}
                </div>
                {!u.is_admin && (
                  <button 
                    onClick={() => handleDeleteUser(u.id)}
                    className="delete-btn"
                  >
                    删除
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 文件列表 */}
      <div className="card">
        <h2>📂 文件列表 ({files.length})</h2>
        <div className="file-list">
          {files.length === 0 ? (
            <p style={{color: '#999', textAlign: 'center'}}>暂无文件，登录后上传第一个文件吧！</p>
          ) : (
            files.map(file => (
              <div key={file.id} className="file-item">
                <div className="file-info">
                  <span className="filename">📄 {file.filename}</span>
                  <span className="size">{(file.file_size / 1024).toFixed(2)} KB</span>
                </div>
                {file.description && (
                  <p className="description">{file.description}</p>
                )}
                {file.tags && (
                  <div className="tags">
                    {file.tags.split(',').map((tag, i) => (
                      <span key={i} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
                <div className="file-actions">
                  <button onClick={() => handleViewFile(file)}>
                    💬 评论
                  </button>
                  <button onClick={() => handleDownload(file.id, file.filename)}>
                    ⬇️ 下载
                  </button>
                  <span className="date">
                    {new Date(file.created_at).toLocaleString('zh-CN')}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 评论面板 */}
      {showComments && selectedFile && (
        <div className="card">
          <h2>💬 评论 - {selectedFile.filename}</h2>
          <div className="comments-section">
            {comments.length === 0 ? (
              <p style={{color: '#999', textAlign: 'center'}}>暂无评论，添加第一条评论吧！</p>
            ) : (
              comments.map(comment => (
                <div key={comment.id} className="comment-item">
                  <p>{comment.content}</p>
                  <small>{new Date(comment.created_at).toLocaleString('zh-CN')}</small>
                </div>
              ))
            )}
          </div>
          <form onSubmit={handleAddComment} className="comment-form">
            <input
              type="text"
              placeholder="添加评论..."
              value={newComment}
              onChange={e => setNewComment(e.target.value)}
            />
            <button type="submit">发送</button>
            <button type="button" onClick={() => setShowComments(false)} className="secondary">
              关闭
            </button>
          </form>
        </div>
      )}

      {/* API 说明 */}
      <div className="card">
        <h2>🔧 QClaw 集成说明</h2>
        <p>1. 登录后点击"生成 API Key"</p>
        <p>2. 复制 API Key 到 QClaw 配置</p>
        <p>3. QClaw 即可访问和上传文件</p>
        <pre>
{`# QClaw 使用示例
curl -X POST http://localhost:8000/api/files/upload-by-api-key \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "file=@file.txt" \\
  -F "description=描述"`}
        </pre>
      </div>
    </div>
  )
}

export default App
