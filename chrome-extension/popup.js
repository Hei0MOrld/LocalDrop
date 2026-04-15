let selectedDevice = null;
let selectedFiles = [];

const deviceList = document.getElementById('deviceList');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const sendBtn = document.getElementById('sendBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const progress = document.getElementById('progress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

// デバイス検索
async function scanDevices() {
  const devices = [];
  const subnet = await getSubnet();
  if (!subnet) {
    statusText.textContent = 'Wi-Fi未接続';
    return;
  }

  statusDot.classList.add('online');
  statusText.textContent = 'デバイスを検索中...';

  const promises = [];
  for (let i = 1; i <= 254; i++) {
    const ip = `${subnet}.${i}`;
    promises.push(
      fetch(`http://${ip}:39876/localdrop-ping`, {
        signal: AbortSignal.timeout(300)
      })
      .then(res => res.json())
      .then(data => {
        if (data.type === 'localdrop') {
          devices.push({ ip, name: data.name, os: data.os });
        }
      })
      .catch(() => {})
    );
  }

  await Promise.all(promises);

  if (devices.length === 0) {
    deviceList.innerHTML = '<div class="no-device">デバイスが見つかりません<br>同じWi-Fiに接続してください</div>';
    statusText.textContent = 'デバイスなし';
  } else {
    statusText.textContent = `${devices.length}台見つかりました`;
    renderDevices(devices);
  }
}

async function getSubnet() {
  try {
    const res = await fetch('http://localhost:39876/localdrop-ping', {
      signal: AbortSignal.timeout(500)
    });
    const data = await res.json();
    return data.subnet;
  } catch {
    return null;
  }
}

function renderDevices(devices) {
  deviceList.innerHTML = devices.map(d => `
    <div class="device-item" data-ip="${d.ip}" data-name="${d.name}">
      <div class="device-icon">${d.os === 'android' ? '📱' : '💻'}</div>
      <div>
        <div class="device-name">${d.name}</div>
        <div class="device-sub">${d.ip}</div>
      </div>
    </div>
  `).join('');

  document.querySelectorAll('.device-item').forEach(item => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.device-item').forEach(i => i.classList.remove('selected'));
      item.classList.add('selected');
      selectedDevice = { ip: item.dataset.ip, name: item.dataset.name };
      updateSendBtn();
    });
  });
}

// ファイル選択
dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
  selectedFiles = Array.from(e.target.files);
  updateDropZone();
  updateSendBtn();
});

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  selectedFiles = Array.from(e.dataTransfer.files);
  updateDropZone();
  updateSendBtn();
});

function updateDropZone() {
  const text = document.getElementById('dropText');
  if (selectedFiles.length > 0) {
    text.textContent = selectedFiles.map(f => f.name).join('\n');
  } else {
    text.textContent = 'ファイルをドロップ\nまたはクリックして選択';
  }
}

function updateSendBtn() {
  if (selectedDevice && selectedFiles.length > 0) {
    sendBtn.disabled = false;
    sendBtn.classList.add('active');
    sendBtn.textContent = `${selectedDevice.name} に送信`;
  } else if (!selectedDevice) {
    sendBtn.disabled = true;
    sendBtn.classList.remove('active');
    sendBtn.textContent = '送信先を選択してください';
  } else {
    sendBtn.disabled = true;
    sendBtn.classList.remove('active');
    sendBtn.textContent = 'ファイルを選択してください';
  }
}

// 送信
sendBtn.addEventListener('click', async () => {
  if (!selectedDevice || selectedFiles.length === 0) return;

  progress.style.display = 'block';
  sendBtn.disabled = true;

  for (let i = 0; i < selectedFiles.length; i++) {
    const file = selectedFiles[i];
    progressText.textContent = `送信中: ${file.name} (${i + 1}/${selectedFiles.length})`;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', `http://${selectedDevice.ip}:39876/receive`);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 100);
          progressFill.style.width = pct + '%';
        }
      };

      await new Promise((resolve, reject) => {
        xhr.onload = () => resolve();
        xhr.onerror = () => reject(new Error('送信失敗'));
        xhr.send(formData);
      });

    } catch (err) {
      progressText.textContent = `エラー: ${file.name} の送信に失敗しました`;
      sendBtn.disabled = false;
      return;
    }
  }

  progressText.textContent = '送信完了！';
  progressFill.style.width = '100%';
  setTimeout(() => {
    progress.style.display = 'none';
    progressFill.style.width = '0%';
    selectedFiles = [];
    updateDropZone();
    sendBtn.disabled = false;
    updateSendBtn();
  }, 2000);
});

// 起動時にスキャン
scanDevices();
setInterval(scanDevices, 10000);