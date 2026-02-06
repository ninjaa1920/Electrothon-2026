// Simple frontend-only auth (localStorage) for demo/testing
document.addEventListener('DOMContentLoaded',()=>{
  const tabs = document.querySelectorAll('.tab');
  const forms = document.querySelectorAll('.form');

  function show(target){
    forms.forEach(f=>{f.classList.toggle('active', f.id===target)});
    tabs.forEach(t=>{t.classList.toggle('active', t.dataset.target===target); t.setAttribute('aria-selected', t.dataset.target===target)});
  }

  tabs.forEach(t=>t.addEventListener('click', ()=> show(t.dataset.target)));
  document.querySelectorAll('[data-switch]').forEach(a=>a.addEventListener('click', e=>{e.preventDefault(); show(e.currentTarget.dataset.switch)}));

  // Helpers
  const usersKey = 'mg_users';
  const currentKey = 'mg_current';

  function readUsers(){
    try{ return JSON.parse(localStorage.getItem(usersKey)||'[]') }catch(e){return[]}
  }
  function writeUsers(u){ localStorage.setItem(usersKey, JSON.stringify(u)) }

  // Register


  // Login


  // Pre-fill if remembered
  try{
    const cur = JSON.parse(localStorage.getItem(currentKey));
    if(cur && cur.email){ document.getElementById('login-email').value = cur.email; document.getElementById('remember').checked=true }
  }catch(e){}

  // Emergency button behavior — copies number and shows guidance
  const emergencyBtn = document.getElementById('emergency-btn');
  const emergencyMsg = document.getElementById('emergency-msg');
  if(emergencyBtn){
    emergencyBtn.addEventListener('click', ()=>{
      const number = '+91123 456 789';
      emergencyMsg.textContent = 'Emergency number copied to clipboard: ' + number;
      emergencyMsg.style.color = '#6b1b5f';
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(number).catch(()=>{});
      }
      setTimeout(()=> emergencyMsg.textContent = '', 6000);
    });
  }
});