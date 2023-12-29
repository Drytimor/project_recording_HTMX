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


class ControllerForm {
    constructor(
        disabledBtn, activateBtn, closeForm,
        thiggerDisabledBtn,thiggerActivateBtn,
         thiggerCloseForm, btnShowForm=null
    ){
        this.disabledBtn = disabledBtn;
        this.activateBtn = activateBtn;
        this.closeForm = closeForm;
        this.thiggerDisabledBtn = thiggerDisabledBtn;
        this.thiggerActivateBtn = thiggerActivateBtn;
        this.thiggerCloseForm = thiggerCloseForm;
        this.btnShowForm = btnShowForm;
    }

    get disable(){
        if (this.btnShowForm){
            this.btnShowForm.setAttribute('disabled', '');
        }
        document.body.removeEventListener(this.thiggerDisabledBtn, this.disabledBtn);
        document.body.addEventListener(this.thiggerCloseForm, this.closeForm);
        document.body.addEventListener(this.thiggerActivateBtn, this.activateBtn);
        document.body.addEventListener('click', this.disabledBtn);
    }

    get activate(){
        this.btnShowForm.removeAttribute('disabled');
        document.body.removeEventListener(this.thiggerActivateBtn, this.activateBtn);
        document.body.removeEventListener(this.thiggerCloseForm, this.closeForm);
        document.body.removeEventListener('click', this.disabledBtn);
        document.body.addEventListener(this.thiggerDisabledBtn, this.disabledBtn);
    }

    get close(){
        this.btnShowForm.removeAttribute('disabled');
        document.body.removeEventListener(this.thiggerCloseForm, this.closeForm);
        document.body.removeEventListener('click', this.disabledBtn);
        document.body.addEventListener(this.thiggerDisabledBtn, this.disabledBtn);
    }
}

// Контроллер формы Employee

document.body.addEventListener('disabledBtnFormEmp', disabledBtnEmp)

const ControllerFormEmppoyee = new ControllerForm(
    disabledBtnEmp,
    activateBtnEmp,
    closeFormEmp,
    'disabledBtnFormEmp',
    'activateBtnFormEmp',
    'closeFormEmp',
)

function disabledBtnEmp(e){
    ControllerFormEmppoyee.btnShowForm = document.querySelector('#btn_show_form_emp');
    ControllerFormEmppoyee.disable
}

function activateBtnEmp(e){
    ControllerFormEmppoyee.activate
}

function closeFormEmp(e){
    ControllerFormEmppoyee.close
}


// Контроллер формы Event

document.body.addEventListener('disabledBtnFormEvent', disabledBtnEvent)

const ControllerFormEvent = new ControllerForm(
    disabledBtnEvent,
    activateBtnEvent,
    closeFormEvent,
    'disabledBtnFormEvent',
    'activateBtnFormEvent',
    'closeFormEvent',
)

function disabledBtnEvent(e){
    ControllerFormEvent.btnShowForm = document.querySelector('#btn_show_form_event');
    ControllerFormEvent.disable
}

function activateBtnEvent(e){
    ControllerFormEvent.activate
}

function closeFormEvent(e){
    ControllerFormEvent.close
}


// Контроллер формы Record

document.body.addEventListener('disabledBtnFormRecord', disabledBtnRecord)

const ControllerFormRecord = new ControllerForm(
    disabledBtnRecord,
    activateBtnRecord,
    closeFormRecord,
    'disabledBtnFormRecord',
    'activateBtnFormRecord',
    'closeFormRecord',
)

function disabledBtnRecord(e){
    ControllerFormRecord.btnShowForm = document.querySelector('#btn_show_form_record');
    ControllerFormRecord.disable
}

function activateBtnRecord(e){
    ControllerFormRecord.activate
}

function closeFormRecord(e){
    ControllerFormRecord.close
}