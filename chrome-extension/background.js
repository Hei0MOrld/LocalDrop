chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'localdrop-send',
    title: 'LocalDropで送信',
    contexts: ['image', 'video', 'audio', 'link']
  });
});

self.addEventListener('message', (event) => {
  console.log('LocalDrop message:', event.data);
});