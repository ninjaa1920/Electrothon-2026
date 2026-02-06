document.addEventListener('DOMContentLoaded', ()=>{
  const form = document.getElementById('policeForm');
  const msg = document.getElementById('message');

  form.addEventListener('submit', e=>{
    e.preventDefault();
    const name = document.getElementById('officerName').value.trim();
    const batch = document.getElementById('batchNo').value.trim();
    if(!name || !batch){
      msg.textContent = 'Please fill both fields.';
      return;
    }
    // simple local save so other pages can read if needed
    try{ localStorage.setItem('police_officer_name', name); localStorage.setItem('police_batch_no', batch); }catch(e){}
    msg.textContent = 'Police details saved.';
    form.animate([{opacity:0.98},{opacity:1}],{duration:200});
  });
});
