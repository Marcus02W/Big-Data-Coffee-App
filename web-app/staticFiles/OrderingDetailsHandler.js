window.onload = () => {
    const formData = new FormData();
    var username = document.cookie
                    .split("; ")
                    .find((row) => row.startsWith("username="))
                    ?.split("=")[1];
    var password = document.cookie
                    .split("; ")
                    .find((row) => row.startsWith("password"))
                    ?.split("=")[1];

    var url = new URL(window.location.href);
    var searchParams = new URLSearchParams(url.search);
    var parameterValue = searchParams.get('parameter');

    formData.append("order_id", parameterValue);
    formData.append("username", username);
    formData.append("password", password);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/ordering_details_api");
    xhr.send(formData);
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){
            response = xhr.responseText;
            response = JSON.parse(response);
            console.log(response);

            // === part for building the logic behind the ordering details table ===
            const tableBody = document.getElementById('table');

            // backend response is parsed into a HTML table format
            response.forEach((row) => {
              const tableRow = document.createElement('tr'); 
            
              row.forEach((cell) => {
                const tableCell = document.createElement('td'); 
                tableCell.textContent = cell;
                tableRow.appendChild(tableCell);
              });
            
              tableBody.appendChild(tableRow);
            });
        }
    }
}