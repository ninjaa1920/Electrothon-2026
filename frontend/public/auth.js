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
  const regForm = document.getElementById('register');
  regForm.addEventListener('submit', e=>{
    e.preventDefault();
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim().toLowerCase();
    const pass = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-confirm').value;
    const msg = document.getElementById('reg-msg');
    msg.className='message';

    if(!name || !email || !pass){ msg.textContent='Please fill all fields.'; msg.classList.add('error'); return }
    if(pass.length<6){ msg.textContent='Password must be at least 6 characters.'; msg.classList.add('error'); return }
    if(pass!==confirm){ msg.textContent='Passwords do not match.'; msg.classList.add('error'); return }

    const users = readUsers();
    if(users.some(u=>u.email===email)){ msg.textContent='An account with that email already exists.'; msg.classList.add('error'); return }

    users.push({name, email, password:pass});
    writeUsers(users);
    msg.textContent='Registration successful. You can now log in to SafeSpace.'; msg.classList.add('success');
    regForm.reset();
    setTimeout(()=> show('login'),800);
  });

  // Login
  const loginForm = document.getElementById('login');
  loginForm.addEventListener('submit', e=>{
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim().toLowerCase();
    const pass = document.getElementById('login-password').value;
    const remember = document.getElementById('remember').checked;
    const msg = document.getElementById('login-msg');
    msg.className='message';

    if(!email||!pass){ msg.textContent='Please fill both fields.'; msg.classList.add('error'); return }
    const users = readUsers();
    const user = users.find(u=>u.email===email && u.password===pass);
    if(!user){ msg.textContent='Invalid credentials.'; msg.classList.add('error'); return }

    // success
    if(remember) localStorage.setItem(currentKey, JSON.stringify({email:user.email,name:user.name}));
    else localStorage.removeItem(currentKey);
    msg.textContent=`Welcome, ${user.name.split(' ')[0]} — stay safe!`; msg.classList.add('success');
    loginForm.reset();
    // In a real app, redirect to protected area here
  });

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