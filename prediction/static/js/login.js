
// Firsbase connect
  // Import the functions you need from the SDKs you need
import {initializeApp} from "https://www.gstatic.com/firebasejs/9.6.2/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.6.2/firebase-auth.js";
import { Database } from "https://www.gstatic.com/firebasejs/9.6.2/firebase-database.js"
const $ = document.querySelector.bind(document);
const $$ = document.querySelectorAll.bind(document);
const username = $('#username');
const password = $('#password');
const signInEmail = $('#sign-in-email');
const signInPwd = $('#sign-in-password');
const email = $('#email');
const confirmPwd = $('#confirm-pwd');

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyDobJg36yOmNfabBQGghbTSWl7_iqpuljo",
    authDomain: "agri-login.firebaseapp.com",
    projectId: "agri-login",
    storageBucket: "agri-login.appspot.com",
    messagingSenderId: "620635385472",
    appId: "1:620635385472:web:228592af7e86d425848065",
    measurementId: "G-PFGCQSKCXL"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth();


// 

const signupLink = document.querySelector(".signup__link");
const loginLink = document.querySelector(".login__link");
const loginForm = document.querySelector(".login");
const signupForm = document.querySelector(".signup");

// validate input
function validateEmail(email) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(email)) {
        return (true)
    }
    alert("You have entered an invalid email address!")
    return (false)
}
function validatePassword(password){
    if(password.length<6){
        alert("Password should have length more than 6 characters");
        return false;
    }
    else return true;
}
function checkPwd(pwd1, pwd2){
    if(pwd1 !== pwd2) {
        alert('Your password is not match')
        return false;
    }
    else return true;
}
function validateUsername(username){
    if(username.length<=0){
        alert("User name can't be null");
        return false;

    }
    else return true;
}
$("#signUp").onsubmit = function(e){
    e.preventDefault();
    if (validateEmail(email.value) && validatePassword(password.value) && checkPwd(password.value, confirmPwd.value) && validateUsername(username.value)) {
        createUserWithEmailAndPassword(auth, email.value, password.value)
            .then((userCredential) => {
                // Signed in 
                const user = userCredential.user;
                e.target.submit()
                // ...
                

            })
            .catch((error) => {
                const errorCode = error.code;
                const errorMessage = error.message;
                // ..

                alert(errorCode);
            });
    }

}
$("#signIn").onsubmit = function (e) {
    e.preventDefault();
    if (validateEmail(signInEmail.value) && validatePassword(signInPwd.value)) {
        signInWithEmailAndPassword(auth, signInEmail.value,signInPwd.value)
            .then((userCredential) => {
                // Signed in 
                const user = userCredential.user;
                // ...
                e.target.submit()

            })
            .catch((error) => {
                const errorCode = error.code;
                const errorMessage = error.message;
                e.preventDefault()
                alert(errorCode)
            });
    }

}

function fetchInfo(username){
    const data = {username: username};
    fetch("/index.html",{
        method: 'post',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
}

