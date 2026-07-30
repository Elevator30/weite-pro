#!/usr/bin/env python3
"""
Task 2: Add photo upload feature to factory-inspection-v2.html
Change from single camera capture to two options: 拍照 + 上传
"""

FILE_PATH = "/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html"

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ====== 1. Add CSS for the new photo buttons ======
old_css = ".ng-photo-add{width:60px;height:60px;border:1.5px dashed #ccc;border-radius:6px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:22px;color:#aaa;background:#fafafa;}"

new_css = """.ng-photo-add{width:60px;height:60px;border:1.5px dashed #ccc;border-radius:6px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:22px;color:#aaa;background:#fafafa;}
.ng-photo-add-btn{width:56px;height:60px;border:1.5px dashed #ccc;border-radius:6px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;font-size:10px;color:#888;background:#fafafa;gap:2px;user-select:none;}
.ng-photo-add-btn .ng-photo-icon{font-size:20px;line-height:1;}
.ng-photo-add-btn:active{background:#f0f0f0;border-color:#aaa;}"""

content = content.replace(old_css, new_css, 1)

# ====== 2. Replace the single "+" button with two buttons ======
old_add_btn = "html += '<div class=\"ng-photo-add\" onclick=\"addNgPhoto(' + itemId + ')\">+</div>';"

new_add_btn = "html += '<div class=\"ng-photo-add-btn\" onclick=\"addNgPhoto(' + itemId + ',true)\"><span class=\"ng-photo-icon\">📷</span><span>拍照</span></div>';"
new_add_btn += "html += '<div class=\"ng-photo-add-btn\" onclick=\"addNgPhoto(' + itemId + ',false)\"><span class=\"ng-photo-icon\">🖼️</span><span>上传</span></div>';"

content = content.replace(old_add_btn, new_add_btn, 1)

# ====== 3. Replace addNgPhoto function with new version that accepts useCamera param ======
old_add_ng_photo = """function addNgPhoto(itemId) {
  var input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.capture = 'environment';
  input.onchange = function(e) {
    var file = e.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function(ev) {
      // Compress image before storing
      var img = new Image();
      img.onload = function() {
        var canvas = document.createElement('canvas');
        var maxW = 800, maxH = 600;
        var w = img.width, h = img.height;
        if (w > maxW) { h = h * maxW / w; w = maxW; }
        if (h > maxH) { w = w * maxH / h; h = maxH; }
        canvas.width = w; canvas.height = h;
        canvas.getContext('2d').drawImage(img, 0, 0, w, h);
        var dataUrl = canvas.toDataURL('image/jpeg', 0.7);
        var task = getCurrentTask();
  if (!task) return;
        if (!task.checks[itemId]) task.checks[itemId] = {};
        if (!task.checks[itemId].photos) task.checks[itemId].photos = [];
        task.checks[itemId].photos.push(dataUrl);
        saveCurrentTask();
        renderZoneContent(currentZoneIndex);
      };
      img.src = ev.target.result;
    };
    reader.readAsDataURL(file);
  };
  input.click();
}"""

new_add_ng_photo = """function addNgPhoto(itemId, useCamera) {
  var input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  if (useCamera) {
    input.capture = 'environment';
  }
  input.onchange = function(e) {
    var file = e.target.files[0];
    if (!file) return;
    processNgPhotoFile(itemId, file);
  };
  input.click();
}

function processNgPhotoFile(itemId, file) {
  var reader = new FileReader();
  reader.onload = function(ev) {
    // Compress image before storing
    var img = new Image();
    img.onload = function() {
      var canvas = document.createElement('canvas');
      var maxW = 800, maxH = 600;
      var w = img.width, h = img.height;
      if (w > maxW) { h = h * maxW / w; w = maxW; }
      if (h > maxH) { w = w * maxH / h; h = maxH; }
      canvas.width = w; canvas.height = h;
      canvas.getContext('2d').drawImage(img, 0, 0, w, h);
      var dataUrl = canvas.toDataURL('image/jpeg', 0.7);
      var task = getCurrentTask();
      if (!task) return;
      if (!task.checks[itemId]) task.checks[itemId] = {};
      if (!task.checks[itemId].photos) task.checks[itemId].photos = [];
      task.checks[itemId].photos.push(dataUrl);
      saveCurrentTask();
      renderZoneContent(currentZoneIndex);
    };
    img.src = ev.target.result;
  };
  reader.readAsDataURL(file);
}"""

content = content.replace(old_add_ng_photo, new_add_ng_photo, 1)

# Write back
with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Task 2 done: factory-inspection-v2.html updated with photo upload feature")
print(f"File size: {len(content)} bytes")

# Verify replacements were made
checks = [
    ("ng-photo-add-btn CSS", ".ng-photo-add-btn" in content),
    ("processNgPhotoFile function", "processNgPhotoFile" in content),
    ("addNgPhoto with useCamera param", "addNgPhoto(itemId, useCamera)" in content),
    ("拍照 button", "📷" in content and "拍照" in content),
    ("上传 button", "🖼️" in content and "上传" in content),
]
for name, result in checks:
    print(f"  {name}: {'✓' if result else '✗'}")
