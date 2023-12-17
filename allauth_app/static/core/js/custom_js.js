const auth_user_nav_bar = `
    <li class="nav-item">
        <a class="ms-2 nav-link text-white"
           role="button"
           hx-get="/profile_htmx/"
           hx-target="#row-main"
           hx-swap="innerHTML"
           hx-push-url="/profile/">
           Профиль
        </a>
    </li>
`

document.body.addEventListener('AuthUser', function(e){
    const navBar = document.querySelector('#nav-bar')
    navBar.innerHTML = auth_user_nav_bar
    htmx.process(document.body)
})


const anonym_user_nav_bar = `
    <li class="nav-item">
        <a class="nav-link text-white"
           hx-get="/accounts/login/"
           role="button"
           hx-target="#modal-form-login"
           data-bs-toggle="modal"
           data-bs-target="#modal-window-login">
           вход
        </a>
    </li>

    <li class="nav-item">
        <a hx-get="/accounts/signup/"
           class="ms-2 nav-link text-white"
           role="button"
           hx-target="#modal-form-signup"
           data-bs-toggle="modal"
           data-bs-target="#modal-window-signup">
           регистрация
        </a>
    </li>
`

document.body.addEventListener('AnonymUser', function(e){
    const navBar = document.querySelector('#nav-bar')
    navBar.innerHTML = anonym_user_nav_bar
    htmx.process(document.body)
})
