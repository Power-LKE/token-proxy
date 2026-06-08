import re
content = open(r'C:\Users\QQ136\Documents\New project\token-proxy-git\static\dashboard.html', encoding='utf-8').read()

# Replace the tabs header - remove register tab
content = content.replace(
    '<div class="tabs">\n      <button class="tab active" onclick="switchTab(\'register\')">注册新用户</button>\n      <button class="tab" onclick="switchTab(\'login\')">已有 API Key</button>\n    </div>',
    '<div class="tabs">\n      <button class="tab active" onclick="switchTab(\'login\')">已有 API Key</button>\n    </div>'
)

# Replace register tab content area  
old_reg_area = '<div class="tab-content active" id="tabRegister">\n      <p style="color:#888;font-size:13px;margin-bottom:12px">输入用户名即可免费注册，获赠启动余额。</p>\n      <div class="row">\n        <div><input type="text" class="inp" id="regName" placeholder="输入用户名" /></div>\n        <div><button class="btn" id="regBtn" onclick="register()">免费注册</button></div>\n      </div>\n      <div class="msg" id="regMsg"></div>\n    </div>\n\n    <div class="tab-content" id="tabLogin">'
new_login_area = '<div class="tab-content active" id="tabLogin">\n      <p style="color:#888;font-size:13px;margin-bottom:12px">注册已关闭。如果你需要账号，请联系管理员。</p>'
content = content.replace(old_reg_area, new_login_area)

# Remove the register() function
content = re.sub(r'function register\(\) \{[^}]*?\n\}', '// Registration disabled', content)

# Remove switchTab for register
content = content.replace("switchTab('register')", "switchTab('login')")

open(r'C:\Users\QQ136\Documents\New project\token-proxy-git\static\dashboard.html', 'w', encoding='utf-8').write(content)
print('OK - dashboard.html updated')
