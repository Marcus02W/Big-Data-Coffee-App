window.onload = () => {
    //console.log(document.cookie);
    const formData = new FormData();

    // accessing the login credentials from the cookie
    var username = document.cookie
                    .split("; ")
                    .find((row) => row.startsWith("username="))
                    ?.split("=")[1];
    var password = document.cookie
                    .split("; ")
                    .find((row) => row.startsWith("password"))
                    ?.split("=")[1];
    formData.append("username", username);
    formData.append("password", password);
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/coffee_shop_page_api");
    xhr.send(formData);

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){
            response = xhr.responseText;
            response = JSON.parse(response);
            console.log(response);

            // === part for building the logic behind the left section (coffee type offerings) ===
            const tableBody = document.getElementById('table-coffee-offerings');

            // backend response is parsed into a HTML table format
            response['coffee_types_overview'].forEach((row) => {
              const tableRow = document.createElement('tr');
            
              row.forEach((cell, index) => {
                const tableCell = document.createElement('td');

                // the second cell is clickable so that coffee shops can easily change their offering by a mouseclick
                if (index === 2) { 
                  const clickableCell = document.createElement('td');
                  clickableCell.textContent = cell;
                  
                  clickableCell.onclick = function() {
                    console.log(row[0], row[1], row[2]);
                    const formDataTypes = new FormData();
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", "/coffee_types_update_api");
                    formDataTypes.append("is_offered", row[2]);
                    formDataTypes.append("size", row[1]);
                    formDataTypes.append("coffee_type", row[0]);
                    formDataTypes.append("shop_id", username);
                    xhr.send(formDataTypes);
                    xhr.onreadystatechange = () => {
                      if (xhr.readyState === 2){
                        location.reload();
                      }
                    }
                    
                  };
                  
                  tableRow.appendChild(clickableCell);
                }
                else{
                  tableCell.textContent = cell;
                  tableRow.appendChild(tableCell);
                }
              });
            
              tableBody.appendChild(tableRow);
            });


            // === part for building the logic behind the top right section (recent orders) ===
            const tableBodyOrders = document.getElementById('table-recent-orders');

            // backend response is parsed into a HTML table format
            response['recent_orders_overview'].forEach((row) => {
              const tableRow = document.createElement('tr');
            
              row.forEach((cell) => {
                const tableCell = document.createElement('td');
                tableCell.textContent = cell;
                tableRow.appendChild(tableCell);
              });
              

              // creating link for viewing ordering details
              tableCell = document.createElement('td');
              var link = document.createElement('a');

              // dynamically insert order_id by row[0]
              link.href = 'ordering_details?parameter=' + row[0];

            
              var linkText = document.createTextNode('View details');
              link.appendChild(linkText);

              tableCell.appendChild(link);

              tableRow.appendChild(tableCell);
            
              tableBodyOrders.appendChild(tableRow);
            });


            // === part for building the logic behind the bottom right section (most critical ratings) ===
            const tableBodyRatings = document.getElementById('table-ratings');

            // backend response is parsed into a HTML table format
            response['ratings_overview'].forEach((row) => {
              const tableRow = document.createElement('tr');
            
              row.forEach((cell) => {
                const tableCell = document.createElement('td');
                tableCell.textContent = cell;
                tableRow.appendChild(tableCell);
              });
            
              tableBodyRatings.appendChild(tableRow);
            });


        }
    }
}