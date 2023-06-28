function signup(){
    const formData = new FormData();
    var firstname = document.getElementById("firstname").value;
    var lastname = document.getElementById("lastname").value;
    var username = document.getElementById("uname").value;
    var password = document.getElementById("psw").value;
    formData.append("firstname", firstname);
    formData.append("lastname", lastname);
    formData.append("username", username);
    formData.append("password", password);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/signup_api");
    xhr.send(formData);

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){
            response = xhr.responseText;
            
            console.log(response);
            if (response=="failed") {
                document.getElementById("response").innerHTML="Registering failed! The user already exists or the id is invalid (has to be numerical)!"
            } 

            else{
                document.getElementById("response").innerHTML="Registration successfull! Explore a world full of the finest coffee."
                document.getElementById("login_link").style.display="inline";
                setTimeout(() => {
                    window.location.href = '/login';
                  }, 1000);
            } 
        }
    }

}