document.addEventListener('DOMContentLoaded', () => {
  const API_URL = window.AURACANVAS_RAG_URL || 'http://127.0.0.1:8001';
  const style = document.createElement('style');
  style.textContent = `
    .ac-chat-button {
      position: fixed;
      right: 24px;
      bottom: 24px;
      z-index: 1000;
      width: 58px;
      height: 58px;
      border: 0;
      border-radius: 50%;
      background: linear-gradient(135deg, #FFF1C5 0%, #D4AF37 50%, #916E18 100%);
      color: #070A12;
      font-size: 22px;
      box-shadow: 0 8px 30px rgba(212, 175, 55, 0.4);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
    }
    .ac-chat-button:hover {
      transform: scale(1.08);
      box-shadow: 0 10px 35px rgba(212, 175, 55, 0.6);
    }
    .ac-chat-panel {
      position: fixed;
      right: 24px;
      bottom: 92px;
      z-index: 1000;
      width: min(370px, calc(100vw - 32px));
      height: 500px;
      background: #0C1322;
      color: #f8fafc;
      border: 1px solid rgba(212, 175, 55, 0.35);
      border-radius: 20px;
      box-shadow: 0 16px 50px rgba(0,0,0,0.85);
      display: none;
      overflow: hidden;
      font-family: Outfit, sans-serif;
    }
    .ac-chat-panel.open {
      display: flex;
      flex-direction: column;
    }
    .ac-chat-head {
      padding: 16px 18px;
      background: #151E2E;
      border-bottom: 1px solid rgba(212, 175, 55, 0.25);
    }
    .ac-chat-head strong {
      display: block;
      color: #E5C158;
      font-size: 15px;
    }
    .ac-chat-head small {
      color: #94a3b8;
      font-size: 11px;
    }
    .ac-chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .ac-chat-msg {
      max-width: 88%;
      padding: 10px 14px;
      border-radius: 14px;
      font-size: 12.5px;
      line-height: 1.45;
      white-space: pre-wrap;
    }
    .ac-chat-msg.bot {
      background: #151E2E;
      color: #e2e8f0;
      border: 1px solid rgba(255,255,255,0.06);
      align-self: flex-start;
    }
    .ac-chat-msg.user {
      background: #D4AF37;
      color: #070A12;
      font-weight: 600;
      align-self: flex-end;
    }
    .ac-chat-form {
      display: flex;
      gap: 8px;
      padding: 12px;
      background: #151E2E;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .ac-chat-form input {
      flex: 1;
      min-width: 0;
      background: #070A12;
      color: #fff;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 9px 12px;
      font-size: 12px;
    }
    .ac-chat-form button {
      border: 0;
      border-radius: 10px;
      background: #D4AF37;
      color: #070A12;
      font-weight: 700;
      padding: 0 14px;
      cursor: pointer;
      font-size: 12px;
    }
  `;
  document.head.appendChild(style);

  const panel = document.createElement('section');
  panel.className = 'ac-chat-panel';
  panel.innerHTML = `
    <div class="ac-chat-head">
      <strong>Live Paintings by Harshita</strong>
      <small>Ask about wedding dates, canvas sizes, pricing (₹), or setup</small>
    </div>
    <div class="ac-chat-messages">
      <div class="ac-chat-msg bot">Hello! I'm Harshita's studio assistant. How can I assist you with your wedding or live event painting inquiry?</div>
    </div>
    <form class="ac-chat-form">
      <input aria-label="Ask about live painting" placeholder="Ask about packages, pricing, dates..." autocomplete="off">
      <button type="submit">Send</button>
    </form>
  `;

  const button = document.createElement('button');
  button.className = 'ac-chat-button';
  button.setAttribute('aria-label', 'Chat with Harshita Assistant');
  button.innerHTML = '<i class="fa-solid fa-palette"></i>';

  document.body.append(button, panel);

  const messages = panel.querySelector('.ac-chat-messages');
  const input = panel.querySelector('input');

  button.addEventListener('click', () => {
    panel.classList.toggle('open');
    if (panel.classList.contains('open')) input.focus();
  });

  panel.querySelector('form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    messages.insertAdjacentHTML('beforeend', `<div class="ac-chat-msg user"></div>`);
    messages.lastElementChild.textContent = message;
    input.value = '';

    const pending = document.createElement('div');
    pending.className = 'ac-chat-msg bot';
    pending.textContent = 'Checking Harshita\'s studio schedule and information...';
    messages.appendChild(pending);
    messages.scrollTop = messages.scrollHeight;

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      if (!response.ok) throw new Error('Chat service offline');
      const data = await response.json();
      pending.textContent = data.answer;
    } catch (error) {
      // Local smart fallback when server is offline
      const msgLower = message.toLowerCase();
      if (msgLower.includes('price') || msgLower.includes('cost') || msgLower.includes('rate') || msgLower.includes('canvas')) {
        pending.textContent = "Harshita offers 4 main canvas sizes:\n• 18x24\" (Intimate): ₹25,000 / $350\n• 24x36\" (Classic - Most Popular): ₹45,000 / $600\n• 30x40\" (Grand Luxury): ₹65,000 / $850\n• 36x48\" (Masterpiece): ₹90,000 / $1,200\n\nA 30% advance deposit reserves your date!";
      } else if (msgLower.includes('book') || msgLower.includes('date') || msgLower.includes('reserve') || msgLower.includes('whatsapp')) {
        pending.textContent = "You can book directly using the 'Book Artist' button on our page or message Harshita directly on WhatsApp at +91 9963473879. A 30% advance deposit is required to lock in your date!";
      } else if (msgLower.includes('travel') || msgLower.includes('destination') || msgLower.includes('udaipur') || msgLower.includes('goa')) {
        pending.textContent = "Yes! Harshita travels worldwide for destination weddings across Goa, Udaipur, Jaipur, Mumbai, Delhi, and internationally. Travel within 50 km is free!";
      } else {
        pending.textContent = "Thank you for asking! Harshita captures weddings, engagements, first dances, and Haldi ceremonies live on canvas. Click 'Book Artist' or check our Price Estimator to lock your date!";
      }
    }
    messages.scrollTop = messages.scrollHeight;
  });
});
