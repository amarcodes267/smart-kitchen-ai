// predictions.js - prediction form helper
async function postPrediction(payload){
  const res = await fetch('/api/prediction/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  return await res.json();
}
