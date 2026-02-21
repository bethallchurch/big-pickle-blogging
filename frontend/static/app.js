let token = localStorage.getItem("token")
if (token) document.getElementById("create-article").style.display = "block"

async function register() {
  const email = document.getElementById("email").value
  const password = document.getElementById("password").value
  const username = document.getElementById("username").value
  const res = await fetch(
    `/api/auth/register?email=${email}&password=${password}&username=${username}`,
    { method: "POST" }
  )
  alert(res.ok ? "Registered! Now login." : "Registration failed.")
}

async function login() {
  const email = document.getElementById("email").value
  const password = document.getElementById("password").value
  const res = await fetch(
    `/api/auth/login?email=${email}&password=${password}`,
    { method: "POST" }
  )
  const data = await res.json()
  if (data.token) {
    localStorage.setItem("token", data.token)
    token = data.token
    document.getElementById("create-article").style.display = "block"
  } else {
    alert("Login failed.")
  }
}

async function createArticle() {
  const title = document.getElementById("title").value
  const body = document.getElementById("body").value
  await fetch(
    `/api/articles?title=${encodeURIComponent(title)}&body=${encodeURIComponent(
      body
    )}`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }
  )
  loadArticles()
}

async function loadArticles() {
  const res = await fetch("/api/articles")
  const articles = await res.json()
  document.getElementById("articles").innerHTML = articles
    .map((a) => `<div><h3>${a.title}</h3><small>${a.created_at}</small></div>`)
    .join("")
}

loadArticles()
