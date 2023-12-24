const navBar = document.querySelector('#nav-bar')

const auth_user_nav_bar = `
    <li class="nav-item">
        <a class="ms-2 nav-link text-white"
           role="button"
           hx-get="/profile/"
           hx-target="#container"
           hx-select="#container"
           hx-swap="outerHTML"
           hx-push-url="/profile/">
           Профиль
        </a>
    </li>
`

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


document.body.addEventListener('AuthUser', insertAuthNavBar)
function insertAuthNavBar(){
    navBar.innerHTML = auth_user_nav_bar
    htmx.process(document.body)
    document.body.removeEventListener('AuthUser', insertAuthNavBar)
    document.body.addEventListener('AnonymUser', insertAnonymNavBar)
}


document.body.addEventListener('AnonymUser', insertAnonymNavBar)
function insertAnonymNavBar(){
    navBar.innerHTML = anonym_user_nav_bar
    htmx.process(document.body)
    document.body.removeEventListener('AnonymUser', insertAnonymNavBar)
    document.body.addEventListener('AuthUser', insertAuthNavBar)
}


const btnControlerEmp = {
    btnShowForm: null,
    btnDeleteForm: null,
    disabledBtn: disabledBtnEmp,
    activateBtn: activateBtnEmp,
    deleteForm: deleteFormEmp,
    thiggerActivateBtn: 'activateBtnFormEmp',
    thiggerDisabledBtn: 'disabledBtnFormEmp',
    get disabled(){
        this.btnShowForm.setAttribute('disabled', '');
        document.body.removeEventListener(this.thiggerDisabledBtn, this.disabledBtn);
        document.body.addEventListener(this.thiggerActivateBtn, this.activateBtn);
        this.btnDeleteForm.addEventListener('click', this.deleteForm);
    },
    get activated(){
        this.btnShowForm.removeAttribute('disabled');
        document.body.removeEventListener(this.thiggerActivateBtn, this.activateBtn);
        this.btnDeleteForm.removeEventListener('click', this.deleteForm);
        document.body.addEventListener(this.thiggerDisabledBtn, this.disabledBtn);
    },
    get deleted(){
        this.btnShowForm.removeAttribute('disabled');
        this.btnDeleteForm.removeEventListener('click', this.deleteForm);
        document.body.addEventListener(this.thiggerDisabledBtn, this.disabledBtn);
    },
}


document.body.addEventListener('disabledBtnFormEmp', disabledBtnEmp)

function disabledBtnEmp(e){
    btnControlerEmp.btnShowForm = document.querySelector('#btn_show_form_emp');
    btnControlerEmp.btnDeleteForm = document.querySelector('#btn_delete_form_emp');
    btnControlerEmp.disabled
}

function activateBtnEmp(e){
    btnControlerEmp.activated
}

function deleteFormEmp(e){
    const form = document.querySelector('#employee-create-form');
    btnControlerEmp.deleted
    form.remove()
}

