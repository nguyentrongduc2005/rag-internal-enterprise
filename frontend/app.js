const API_BASE = window.location.origin;

const state = {
  token: localStorage.getItem("rag_token") || "",
  user: null,
  authMode: "login",
  conversationId: null,
  selectedDocumentId: localStorage.getItem("rag_selected_document_id") || "",
  sourcesByConversation: new Map(),
};

const els = {
  userLabel: document.querySelector("#userLabel"),
  logoutBtn: document.querySelector("#logoutBtn"),
  authPanel: document.querySelector("#authPanel"),
  authForm: document.querySelector("#authForm"),
  authSubmit: document.querySelector("#authSubmit"),
  fullNameInput: document.querySelector("#fullNameInput"),
  emailInput: document.querySelector("#emailInput"),
  passwordInput: document.querySelector("#passwordInput"),
  documentPanel: document.querySelector("#documentPanel"),
  uploadForm: document.querySelector("#uploadForm"),
  fileInput: document.querySelector("#fileInput"),
  documentList: document.querySelector("#documentList"),
  refreshDocsBtn: document.querySelector("#refreshDocsBtn"),
  conversationLabel: document.querySelector("#conversationLabel"),
  conversationList: document.querySelector("#conversationList"),
  refreshConversationsBtn: document.querySelector("#refreshConversationsBtn"),
  newChatBtn: document.querySelector("#newChatBtn"),
  messages: document.querySelector("#messages"),
  chatForm: document.querySelector("#chatForm"),
  questionInput: document.querySelector("#questionInput"),
  sendBtn: document.querySelector("#sendBtn"),
  toast: document.querySelector("#toast"),
};

document.querySelectorAll("[data-auth-tab]").forEach((button) => {
  button.addEventListener("click", () => setAuthMode(button.dataset.authTab));
});

els.authForm.addEventListener("submit", handleAuth);
els.logoutBtn.addEventListener("click", logout);
els.uploadForm.addEventListener("submit", uploadDocument);
els.refreshDocsBtn.addEventListener("click", loadDocuments);
els.refreshConversationsBtn.addEventListener("click", loadConversations);
els.newChatBtn.addEventListener("click", startNewChat);
els.chatForm.addEventListener("submit", sendMessage);

boot();

async function boot() {
  setAuthMode("login");
  if (!state.token) {
    renderAuthState();
    return;
  }

  try {
    state.user = await api("/auth/me");
    renderAuthState();
    await Promise.all([loadDocuments(), loadConversations()]);
  } catch (error) {
    logout();
    showToast(error.message);
  }
}

function setAuthMode(mode) {
  state.authMode = mode;
  document.querySelectorAll("[data-auth-tab]").forEach((button) => {
    button.classList.toggle("active", button.dataset.authTab === mode);
  });
  els.fullNameInput.hidden = mode !== "register";
  els.authSubmit.textContent = mode === "register" ? "Đăng ký" : "Đăng nhập";
}

async function handleAuth(event) {
  event.preventDefault();
  const email = els.emailInput.value.trim();
  const password = els.passwordInput.value;
  const fullName = els.fullNameInput.value.trim();

  try {
    if (state.authMode === "register") {
      await api("/auth/register", {
        method: "POST",
        body: { email, password, full_name: fullName || null },
      });
    }

    const token = await api("/auth/login", {
      method: "POST",
      body: { email, password },
      skipAuth: true,
    });
    state.token = token.access_token;
    localStorage.setItem("rag_token", state.token);
    state.user = await api("/auth/me");
    renderAuthState();
    await Promise.all([loadDocuments(), loadConversations()]);
    showToast("Đã đăng nhập");
  } catch (error) {
    showToast(error.message);
  }
}

function renderAuthState() {
  const loggedIn = Boolean(state.user);
  els.authPanel.hidden = loggedIn;
  els.documentPanel.hidden = !loggedIn;
  els.logoutBtn.hidden = !loggedIn;
  els.userLabel.textContent = loggedIn
    ? `${state.user.full_name || state.user.email} · ${state.user.role}`
    : "Chưa đăng nhập";
  els.chatForm.hidden = !loggedIn;
}

async function loadDocuments() {
  if (!state.token) return;
  const documents = await api("/documents");
  if (state.selectedDocumentId && !documents.some((doc) => doc.id === state.selectedDocumentId)) {
    state.selectedDocumentId = "";
    localStorage.removeItem("rag_selected_document_id");
  }
  els.documentList.innerHTML = documents.length
    ? documents.map(renderDocument).join("")
    : '<div class="item"><div class="item-meta">Chưa có tài liệu</div></div>';

  els.documentList.querySelectorAll("[data-document-id]").forEach((item) => {
    item.addEventListener("click", () => selectDocument(item.dataset.documentId));
  });
}

function renderDocument(doc) {
  const active = doc.id === state.selectedDocumentId ? " active" : "";
  return `
    <button class="item${active}" type="button" data-document-id="${doc.id}">
      <div class="item-title">${escapeHtml(doc.file_name)}</div>
      <div class="item-meta">${escapeHtml(doc.status)} · ${formatBytes(doc.size_bytes)}</div>
    </button>
  `;
}

function selectDocument(id) {
  state.selectedDocumentId = state.selectedDocumentId === id ? "" : id;
  if (state.selectedDocumentId) {
    localStorage.setItem("rag_selected_document_id", state.selectedDocumentId);
    showToast("Đã chọn tài liệu cho chat");
  } else {
    localStorage.removeItem("rag_selected_document_id");
    showToast("Đã bỏ chọn tài liệu");
  }
  loadDocuments();
}

async function uploadDocument(event) {
  event.preventDefault();
  const file = els.fileInput.files[0];
  if (!file) {
    showToast("Chọn file trước khi upload");
    return;
  }

  const body = new FormData();
  body.append("file", file);
  try {
    await fetchApi("/documents/upload", { method: "POST", body });
    els.fileInput.value = "";
    await loadDocuments();
    showToast("Đã upload tài liệu");
  } catch (error) {
    showToast(error.message);
  }
}

async function loadConversations() {
  if (!state.token) return;
  const conversations = await api("/chat/conversations");
  els.conversationList.innerHTML = conversations.length
    ? conversations.map(renderConversation).join("")
    : '<div class="item"><div class="item-meta">Chưa có hội thoại</div></div>';

  els.conversationList.querySelectorAll("[data-conversation-id]").forEach((item) => {
    item.addEventListener("click", () => selectConversation(item.dataset.conversationId));
  });
}

function renderConversation(conversation) {
  const active = conversation.id === state.conversationId ? " active" : "";
  return `
    <button class="item${active}" data-conversation-id="${conversation.id}">
      <div class="item-title">${escapeHtml(conversation.title || "Không tiêu đề")}</div>
      <div class="item-meta">${new Date(conversation.updated_at).toLocaleString()}</div>
    </button>
  `;
}

async function selectConversation(id) {
  state.conversationId = id;
  els.conversationLabel.textContent = `Conversation ${id.slice(0, 8)}`;
  const messages = await api(`/chat/conversations/${id}/messages?limit=50`);
  clearMessages();
  messages.forEach((message) => addMessage(message.role, message.content));
  await loadConversations();
}

function startNewChat() {
  state.conversationId = null;
  els.conversationLabel.textContent = "Tạo câu hỏi mới để bắt đầu";
  clearMessages();
}

async function sendMessage(event) {
  event.preventDefault();
  const question = els.questionInput.value.trim();
  if (!question || !state.token) return;

  els.questionInput.value = "";
  els.sendBtn.disabled = true;
  addMessage("user", question);
  const assistantNode = addMessage("assistant", "");

  try {
    await streamChat(question, assistantNode);
    await loadConversations();
  } catch (error) {
    assistantNode.textContent = "Lỗi: " + error.message;
  } finally {
    els.sendBtn.disabled = false;
    els.questionInput.focus();
  }
}

async function streamChat(question, assistantNode) {
  const response = await fetchApi("/chat/stream", {
    method: "POST",
    body: JSON.stringify({
      question,
      conversation_id: state.conversationId,
      document_id: state.selectedDocumentId || null,
      k: 5,
    }),
    headers: { "Content-Type": "application/json" },
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let sources = [];

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop();

    for (const line of lines) {
      if (!line.trim()) continue;
      const event = JSON.parse(line);
      if (event.type === "meta") {
        state.conversationId = event.conversation_id;
        sources = event.sources || [];
        els.conversationLabel.textContent = `Conversation ${state.conversationId.slice(0, 8)}`;
      }
      if (event.type === "token") {
        assistantNode.textContent += event.content;
        scrollMessages();
      }
      if (event.type === "done") {
        appendSources(assistantNode, sources);
      }
      if (event.type === "error") {
        throw new Error(event.detail || "Streaming failed");
      }
    }
  }
}

function addMessage(role, content) {
  removeEmptyState();
  const node = document.createElement("div");
  node.className = `message ${role}`;
  node.textContent = content;
  els.messages.appendChild(node);
  scrollMessages();
  return node;
}

function appendSources(messageNode, sources) {
  if (!sources.length) return;
  const sourcesNode = document.createElement("div");
  sourcesNode.className = "sources";
  sourcesNode.textContent = sources
    .slice(0, 3)
    .map((source, index) => `${index + 1}. ${source.filename} · score ${source.score.toFixed(3)}`)
    .join("\n");
  messageNode.appendChild(sourcesNode);
}

function clearMessages() {
  els.messages.innerHTML = '<div class="empty-state">Đặt câu hỏi để bắt đầu hội thoại.</div>';
}

function removeEmptyState() {
  const empty = els.messages.querySelector(".empty-state");
  if (empty) empty.remove();
}

function scrollMessages() {
  els.messages.scrollTop = els.messages.scrollHeight;
}

async function api(path, options = {}) {
  const response = await fetchApi(path, {
    ...options,
    body: options.body && !(options.body instanceof FormData) ? JSON.stringify(options.body) : options.body,
    headers: {
      "Content-Type": options.body instanceof FormData ? undefined : "application/json",
      ...(options.headers || {}),
    },
  });
  return response.json();
}

async function fetchApi(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (headers["Content-Type"] === undefined) delete headers["Content-Type"];
  if (state.token && !options.skipAuth) headers.Authorization = `Bearer ${state.token}`;

  const response = await fetch(API_BASE + path, { ...options, headers });
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }
  return response;
}

function logout() {
  localStorage.removeItem("rag_token");
  state.token = "";
  state.user = null;
  state.conversationId = null;
  state.selectedDocumentId = "";
  renderAuthState();
  clearMessages();
  els.documentList.innerHTML = "";
  els.conversationList.innerHTML = "";
  localStorage.removeItem("rag_selected_document_id");
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    els.toast.hidden = true;
  }, 3200);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`;
}
