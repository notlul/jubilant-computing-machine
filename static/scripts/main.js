//Display
dpnm = document.getElementById('displayName');
q1 = document.getElementById('g1');
q2 = document.getElementById('g2');

//Creation
cq1 = document.getElementById('q1');
cq2 = document.getElementById('q2');
nm = document.getElementById('name');

let currentQuestionId = null;
function createQuestion(event){
    event.preventDefault();
    $.ajax({
        url: `/createQuestion/${nm.value}/${cq1.value}/${cq2.value}`,
        type: 'POST',
        success: function(response) {
            console.log("Success!", response);
        },
        error: function(error) {
            console.error("Something went wrong", error);
        }
    })
}
function genQuestion(){
    $.ajax({
        url: "/genQuestion",
        type: 'GET',
        success: function(response){
            currentQuestionId = 999;
            console.log(response)
            loadQuestion(response[0],response[1],response[2])
        },
        error: function(error){
            console.log("NEKI KLE NE STIMA")
        }
    })
}
function getQuestion(){
    $.ajax({
        url: `/getQuestion`,
        type: 'GET',
        success: function(response) {
            currentQuestionId = response['id'];
            console.log(response)
            loadQuestion(response['name'], response['option1'], response['option2'])
        },
        error: function(error) {
            console.error("Something went wrong", error);
        }
    })
}
function choice1() {
    if(currentQuestionId==999){
        genQuestion();
        q1.disabled = true;
        q2.disabled = true;
        return;
    }
    if(!currentQuestionId) return;
    sendVote('c1');
}

function choice2() {
    if(currentQuestionId==999){
        genQuestion();
        q1.disabled = true;
        q2.disabled = true;
        return;
    }
    if(!currentQuestionId) return;
    sendVote('c2');
}

function sendVote(choice) {
    $.ajax({
        url: `/vote/${currentQuestionId}/${choice}`,
        type: 'POST',
        success: function(response) {
            document.getElementById('g1').innerText = `${response['option1']} (${response['c1']})`;
            document.getElementById('g2').innerText = `${response['option2']} (${response['c2']})`;
            
            document.getElementById('g1').disabled = true;
            document.getElementById('g2').disabled = true;
        }
    });
}
function loadQuestion(name, o1, o2){
    const btn1 = document.getElementById('g1');
    const btn2 = document.getElementById('g2');
    dpnm.innerText = name
    q1.innerText = o1
    q2.innerText = o2
    btn1.disabled = false;
    btn2.disabled = false;
}