// recommendations.js - request recommendations
async function getRecommendation(payload){
  const res = await fetch('/api/recommendation/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  return await res.json();
}
