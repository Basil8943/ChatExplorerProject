// Variables

let selectedUserId = "";
let current_domain = "http://127.0.0.1:8000/"

// Api call Method

function api_call(url){
    return new Promise(function (resolve, reject) {
        fetch(url)
          .then(response => response.json())
          .then(data => {
            resolve(data);
          })
          .catch(error => {
            reject(error);
          });
      });
}


window.onload = function () {

    var fixedCard = $("#fixedCard");
var initialTop = 83; // Initial top position
var scrollThreshold = 50; // Scroll threshold to trigger the change
var animationDuration = 100; // Animation duration in milliseconds

$(window).scroll(function() {
    var scrollTop = $(window).scrollTop();

    if (scrollTop >= scrollThreshold && fixedCard.css("top") !== "10px") {
        // Change the top position after scrolling 50px or more with animation
        fixedCard.animate({ top: "10px" }, animationDuration);
    } else if (scrollTop < scrollThreshold && fixedCard.css("top") !== initialTop + "px") {
        // Reset to the initial top position if less than 50px scrolled with animation
        fixedCard.animate({ top: initialTop + "px" }, animationDuration);
    }

    // Reset to the initial top position when scrolling back to the top
    if (scrollTop === 0 && fixedCard.css("top") !== initialTop + "px") {
        fixedCard.animate({ top: initialTop + "px" }, animationDuration);
    }
});

    
    var selectedValue = $('#userSelect').val();
    console.log(selectedValue)
    console.log("selectedvalue")

    handleSelectChange();

    
    // Add a change event listener to the select box
    $('#userSelect').on('change', handleSelectChange);

    // Function to handle the change event
    function handleSelectChange() {
        const chatContainer = $('#chat-container');
        chatContainer.empty();
        // Get the selected value
        selectedUserId = $('#userSelect').val();
        console.log(selectedValue)
        let url = `${current_domain}/getsessions/${selectedUserId}`;
        const sessionContainer = $('#session-container');
        sessionContainer.empty();
        $('#session-alert').addClass('d-none');
        $('.loader').removeClass('d-none');
        api_call(url)
            .then(session_list => {
                // The first function has completed, and you have the session_list
                RenderSessionDetails(session_list);
                
            })
            .catch(error => {
                // Handle any errors from the API call
                console.error("API call error:", error);
            });
    }


    // For render Session Data

    function RenderSessionDetails(data){
        const sessionContainer = $('#session-container');
        $('.loader').addClass('d-none');
        sessionContainer.empty();
        if(data.length == 0){
            $('#session-alert').removeClass('d-none');
        }
        else{
            $('#session-alert').addClass('d-none');
        }
        $.each(data, function (key, value) {
            // Parse the original date string
            const originalDate = new Date(value.latest_created);

            // Format the date as "Dec 9, 8:35 PM"
            const formattedDate = originalDate.toLocaleString('en-US', {
            month: 'short',  // Short month name (e.g., Dec)
            day: 'numeric',   // Day of the month (e.g., 9)
            hour: 'numeric',  // Hour (e.g., 8)
            minute: '2-digit', // Minutes (e.g., 35)
            hour12: true      // Use 12-hour clock (AM/PM)
            });
            const sessionItem = `
            <div class="d-lg-flex align-items-center justify-content-between session-item-flex mb-1" id="${value.sessionId}" onClick="GetChatResults('${value.sessionId}')">
                <div>
                <h6 class="session-item-text m-0">${value.sessionId}</h6>
                </div>
                <div>
                <h6 class="text-muted session-item-text m-0">${formattedDate}</h6>
                </div>
            </div>
            `;
            sessionContainer.append(sessionItem);
        });
    }

};


function toggleCard(cardId) {
    // Hide all cards
    document.getElementById('signupcard').style.display = 'none';
    document.getElementById('logincard').style.display = 'none';

    // Show the selected card
    document.getElementById(cardId).style.display = 'block';
}


// Method For Getting Chat Result with Session Id and UserId

function GetChatResults(session_id){
    $(".session-item-flex").removeClass('active-session');
    $(`#${session_id}`).addClass('active-session');
    let url = `${current_domain}getchatresults/${selectedUserId}/${session_id}`;
    api_call(url)
            .then(response => {
                // The first function has completed, and you have the session_list
                console.log("Response",response);
                if(response.length > 0){
                    RenderChatSession(response);
                }
               
                
            })
            .catch(error => {
                // Handle any errors from the API call
                console.error("API call error:", error);
            });
}


function RenderChatSession(data){
    const chatContainer = $('#chat-container');
    chatContainer.empty();
    $.each(data, function (key, value) {
        const chatitem = `
        <div class="d-lg-flex my-3">
            <div class="text-primary text-nowrap chat-username ">
                <h6 class="m-0">${value.user_name} :</h6>
            </div>

            <div class="ms-lg-2 ms-0">
                <h6 class="m-0">${value.message}</h6>
            </div>

        </div>
            `;
        chatContainer.append(chatitem);
    })
}
