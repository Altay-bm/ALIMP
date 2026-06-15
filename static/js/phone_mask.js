// Phone mask: formats input as 8 (XXX) XXX-XX-XX
// Attach to inputs with class="phone"
(function(){
  function formatPhoneValue(value){
    let d = String(value||'').replace(/\D/g,'');
    if(!d) return '';
    if(d[0]==='+') d=d.slice(1);
    // normalize leading 7 -> 8, otherwise ensure leading 8
    if(d[0]=='7') d = '8' + d.slice(1);
    if(d[0] !== '8') d = '8' + d;
    d = d.slice(0,11); // 11 digits: 8 + 10
    let out = d[0] || '';
    if(d.length > 1){
      out += ' (' + d.slice(1, Math.min(4,d.length));
      if(d.length >= 4) out += ')';
    }
    if(d.length > 4){
      out += ' ' + d.slice(4, Math.min(7,d.length));
    }
    if(d.length > 7){
      out += '-' + d.slice(7, Math.min(9,d.length));
    }
    if(d.length > 9){
      out += '-' + d.slice(9, 11);
    }
    return out;
  }

  function onInput(e){
    const el = e.target;
    if(!el.classList || !el.classList.contains('phone')) return;
    const start = el.selectionStart;
    const prev = el.value;
    const formatted = formatPhoneValue(prev);
    el.value = formatted;
    // move caret to end for simplicity
    el.setSelectionRange(el.value.length, el.value.length);
  }

  function onPaste(e){
    const el = e.target;
    if(!el.classList || !el.classList.contains('phone')) return;
    const paste = (e.clipboardData || window.clipboardData).getData('text');
    e.preventDefault();
    el.value = formatPhoneValue(paste);
  }

  document.addEventListener('input', onInput, true);
  document.addEventListener('paste', onPaste, true);

  // initialize existing inputs on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('input.phone').forEach(function(i){
      i.value = formatPhoneValue(i.value);
    });
  });
})();
