content = open(r'C:\Users\QQ136\Documents\New project\token-proxy-git\static\index.html', encoding="utf-8").read()

# Replace "立即免费试用" buttons
content = content.replace("\u7acb\u5373\u514d\u8d39\u8bd5\u7528 \u2192", "\u8054\u7cfb\u7ba1\u7406\u5458 \u2192")

# Replace "免费试用" in the nav
content = content.replace("\u514d\u8d39\u8bd5\u7528", "\u8054\u7cfb\u7ba1\u7406\u5458")

# Replace hero button link
content = content.replace('href="/dashboard" class="btn"', 'href="/static/user.html" class="btn"')

# Remove the badge
content = content.replace('\u706b \u65b0\u7528\u6237\u6ce8\u518c\u5373\u9001\u4f53\u9a8c\u91d1', '\u706b \u9700\u8981\u8d26\u53f7\uff1f\u8054\u7cfb\u7ba1\u7406\u5458\u5f00\u901a')

# Update step 2 text
content = content.replace("\u6ce8\u518c\u9886\u53d6\u5bc6\u94a5", "\u83b7\u53d6 API Key")
content = content.replace("\u70b9\u51fb\u4e0b\u65b9\u201c\u514d\u8d39\u8bd5\u7528\u201d\uff0c\u8f93\u5165\u7528\u6237\u540d\u5373\u53ef\u6ce8\u518c\uff0c\u81ea\u52a8\u83b7\u5f97 API Key", "\u8054\u7cfb\u7ba1\u7406\u5458\u4e3a\u4f60\u5f00\u901a\u8d26\u53f7\uff0c\u83b7\u53d6\u4e13\u5c5e API Key")
content = content.replace('<a href="/dashboard" style="color:#4f46e5">\u7acb\u5373\u6ce8\u518c \u2192</a>', '<a href="/static/user.html" style="color:#4f46e5">\u67e5\u770b\u4f7f\u7528\u6559\u7a0b \u2192</a>')

# Update step 3
content = content.replace("\u4f60\u6ce8\u518c\u5f97\u5230\u7684 Key", "\u7ba1\u7406\u5458\u7ed9\u4f60\u7684 Key")

# Update CTA button at bottom
content = content.replace('<a href="/dashboard" class="hero btn" style="display:inline-block">\u514d\u8d39\u8bd5\u7528 \u2192</a>', '')

# Remove the "新用户赠送体验金" feature card
old_card = '\u65b0\u7528\u6237\u8d60\u9001\u4f53\u9a8c\u91d1'
card_start = content.find(old_card)
if card_start > 0:
    # Find the start of this feature card div
    div_start = content.rfind('<div class="feature-card">', 0, card_start)
    div_end = content.find('</div>', card_start) + 6
    if div_start > 0:
        # Find the 6th closing div (there might be nested divs)
        count = 0
        end = div_end
        for _ in range(5):
            end = content.find('</div>', end) + 6
        content = content[:div_start] + content[end:]

# Update the FAQ about pricing
content = content.replace("\u6ce8\u518c\u5373\u8d60\u9001\u8d77\u6b65\u4f59\u989d\uff0c\u53ef\u4ee5\u5148\u514d\u8d39\u8bd5\u7528\u6765\u611f\u53d7\u3002", "\u8054\u7cfb\u7ba1\u7406\u5458\u5f00\u901a\u8d26\u53f7\u3002\u6309\u91cf\u8ba1\u8d39\uff0c\u7528\u591a\u5c11\u6263\u591a\u5c11\u3002")

open(r'C:\Users\QQ136\Documents\New project\token-proxy-git\static\index.html', 'w', encoding='utf-8').write(content)
print('OK - index.html updated')
