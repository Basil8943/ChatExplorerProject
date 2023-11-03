// Variables

let selectedUserId = "";
let selectedSessionId = "";
let current_domain = "http://127.0.0.1:8000/"
let session_list = []
// Api call Method

function get_api_call(url){
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




function post_api_call(url,data){
    return new Promise(function (resolve, reject) {
        fetch(url, {
          method: 'POST',
          body: JSON.stringify(data),
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken() 
            // You can add more headers if needed
          },
        })
          .then(response => {
            if (!response.ok) {
              // Handle non-OK responses here
              reject(response.statusText);
              return;
            }
            return response.json();
          })
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





// Click Events

    // Add a change event listener to the select box
    $('#choose-btn').on('click', GetSessionList);

    // Add a click event to save commented data
    $('#comment-btn').on('click', SaveCommentToDB);


    // Disabling of comment button based on text-area input
    $('#comment-area').on('input', ActivateCommentbtn);

    
    var selectedValue = $('#userSelect').val();

    GetSessionList();

    
    // Add a change event listener to the select box

    // Function to handle the change event
// Function to handle the change event
function GetSessionList() {
    $('.comment-section').addClass('d-none');
    // Reset Chat Content Values
    const chatContainer = $('#chat-container');
    chatContainer.empty();
    $('#message-alert').removeClass('d-none');
    // Get the selected value
    selectedUserId = $('#userSelect').val();
    let url = `${current_domain}/getsessions/${selectedUserId}`;
    const sessionContainer = $('#session-container');
    sessionContainer.empty();
    $('#session-alert').addClass('d-none');
    $('.loader').removeClass('d-none');
    const commentContainer = $('#comment-container');
    commentContainer.empty();
    get_api_call(url)
        .then(response => {
            session_list = response;
            // The first function has completed, and you have the session_list
            RenderSessionDetails(session_list);
            if(session_list.length > 0){
                GetChatResults(session_list[0].sessionId);
            }           
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
    // Hide onecard cards
    document.getElementById('signupcard').style.display = 'none';
    document.getElementById('logincard').style.display = 'none';
    // Show the selected card
    document.getElementById(cardId).style.display = 'block';
}






// Method For Getting Chat Result with Session Id and UserId

// Method For Getting Chat Result with Session Id and UserId

function GetChatResults(session_id){
    selectedSessionId = session_id;
    $(".session-item-flex").removeClass('active-session');
    $(`#${session_id}`).addClass('active-session');
    $('.chat-alert-overlay').removeClass('d-none');
    $('#message-alert').addClass('d-none');
    let url = `${current_domain}/getchatresults/${selectedUserId}/${session_id}`;
    get_api_call(url)
            .then(response => {
                $('.chat-alert-overlay').addClass('d-none');
                // The first function has completed, and you have the session_list
                console.log("Response",response);
                if(response.chat_data.length > 0){
                    $('#message-alert').addClass('d-none');
                    $('.comment-section').removeClass('d-none');
                    RenderChatSession(response.chat_data);
                }
                else{
                    $('#message-alert').removeClass('d-none');
                }                
                if(response.comment_data.length > 0){
                    RenderCommentSession(response.comment_data);
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
                <h6 class="m-0 message-text">${value.message}</h6>
            </div>
        </div>
            `;
        chatContainer.append(chatitem);
    })
}

function RenderCommentSession(data){
    const commentContainer = $('#comment-container');
    commentContainer.empty();
    $.each(data, function (key, value) {
        const commentitem = `
        <div class="card-body chat-card mt-3">
                        <div class="card-body comment-card py-1">
                            <div id="comment-container"></div>
                            <div class="comment-by-row">
                                <span class="cbytext">Commented by </span>
                                <strong class="commentby">${value.user_name}</strong>
                            </div>
                            <div class="comment-box pt-1 ps-3">
                                    <p class="commenttext">${value.comment}</p>
                            </div>
                            <div class="row">
                                <div class="col-md-11">
                                    <div class="textareabox d-none replaysection">
                                        <textarea class="textareainput w-100" style=""></textarea>
                                    </div>
                                </div>
                                <div class="col-md-1 mt-auto">
                                    <div class="replaydiv text-end replayactive">
                                        <span class="replaytext px-1">
                                            <i class="fa-solid fa-reply pe-1 fa-sm"></i>
                                            Replay
                                        </span>
                                    </div>
                                    <div class="d-none replaysection">
                                        <div class="replaydiv text-center mb-1">
                                            <span class="replaytext px-1">
                                                Cancel
                                            </span>
                                        </div>
                                        <div class="replaydiv text-center">
                                            <span class="replaytext px-1">
                                                Comment
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="ms-5">
                        <div class="card-body comment-card px-3 py-1 mb-3">
                            <div id="comment-container"></div>
                            <div class="comment-by-row">
                                <span class="cbytext">Responsed by </span>
                                <strong class="commentby">${value.user_name}</strong>
                            </div>
                            <div class="comment-box pt-1 ps-3">
                                    <p class="commenttext">${value.comment}</p>
                            </div>
                            <div class="row">
                            <div class="col-md-11">
                                <div class="textareabox d-none replaysection">
                                    <textarea class="textareainput w-100" style=""></textarea>
                                </div>
                            </div>
                            <div class="col-md-1 mt-auto">
                                <div class="replaydiv text-end replayactive">
                                    <span class="replaytext px-1">
                                        <i class="fa-solid fa-reply pe-1 fa-sm"></i>
                                        Replay
                                    </span>
                                </div>
                                <div class="d-none replaysection">
                                    <div class="replaydiv text-center mb-1">
                                        <span class="replaytext px-1">
                                            Cancel
                                        </span>
                                    </div>
                                    <div class="replaydiv text-center">
                                        <span class="replaytext px-1">
                                            Comment
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        </div>
                    </div>
            `;
            commentContainer.append(commentitem);
    })
}




// method for saving comment to DB
function SaveCommentToDB(){
    let comment = $("#comment-area").val()
    const save_comment_url = `${current_domain}/save_comment`
    // Spinner Loading
    $('.spinner-comment-btn').removeClass('d-none');
    // Disabling Comment Button
    $("#comment-btn").prop("disabled", true);
    
    let data = {
        "comment": comment,
        "session_id":selectedSessionId,
        "user_id":selectedUserId
    }
    post_api_call(save_comment_url,data)
            .then(response => {
                console.log("OuterResponce",response)
                if(response.status == "success"){
                    showtoastnotification("Comment saved successfully.","#49c282")
                    $("#comment-area").val("");
                    $('.spinner-comment-btn').addClass('d-none');
                    GetUpdatedComments(selectedSessionId,selectedUserId)
                    console.log("InnerResponce",response)
                }       
            })
            .catch(error => {
                // Handle any errors from the API call
                console.error("API call error:", error);
            });
}

// Get CSRF Token From Cookie

function getCSRFToken() {
    const name = "csrftoken=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    for (let i = 0; i < cookieArray.length; i++) {
      let cookie = cookieArray[i].trim();
      if (cookie.indexOf(name) === 0) {
        return cookie.substring(name.length, cookie.length);
      }
    }
    return "";
  }

function GetUpdatedComments(selectedSessionId,selectedUserId){
    let url = `${current_domain}/getcomments/${selectedUserId}/${selectedSessionId}`;
    get_api_call(url)
        .then(response => {
            // The first function has completed, and you have the session_list
            console.log("Response",response);                
            if(response.comment_data.length > 0){
                RenderCommentSession(response.comment_data);
            }               
        })
        .catch(error => {
            // Handle any errors from the API call
            console.error("API call error:", error);
        });
}


function showtoastnotification(message,color){
    Toastify({
        text: message,
        style: {
            background: color,
        },
        position: "center",
      }).showToast();
}


