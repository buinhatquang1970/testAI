let countdownTimer;
let timeRemaining = 5 * 60; // 5 phút
let quizStarted = false;
let quizStartTime;

window.onload = function() {
    disableQuiz(true);
};

function disableQuiz(isDisabled) {
    document.querySelectorAll('input[type=radio]').forEach(input => input.disabled = isDisabled);
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = isDisabled;
    submitBtn.style.opacity = isDisabled ? '0.5' : '1';

    document.querySelectorAll('.question').forEach(q => q.style.opacity = isDisabled ? '0.4' : '1');
}

function startQuiz() {
    const nameInput = document.getElementById("participant-name").value.trim();
    if (nameInput === "") {
        alert("Vui lòng nhập tên trước khi bắt đầu bài thi!");
        return;
    }

    quizStarted = true;
    quizStartTime = new Date();

    disableQuiz(false);

    // Vô hiệu hóa nút bắt đầu
    const startBtn = document.getElementById("start-btn");
    startBtn.disabled = true;
    startBtn.style.opacity = "0.5";

    startCountdown();
}

function startCountdown() {
    updateTimerDisplay();

    countdownTimer = setInterval(() => {
        timeRemaining--;
        updateTimerDisplay();

        if (timeRemaining <= 0) {
            clearInterval(countdownTimer);
            alert("Hết giờ!");
            checkAnswers();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    document.getElementById("countdown").innerText = `${minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
}

async function checkAnswers() {
    if (!quizStarted) {
        alert("Bạn chưa bắt đầu bài thi!");
        return;
    }

    clearInterval(countdownTimer);

    let score = 0;
    const questions = document.querySelectorAll('.question');

    questions.forEach(questionDiv => {
        const correct = questionDiv.getAttribute('data-correct');
        const questionName = questionDiv.querySelector('input[type=radio]').name;

        const options = document.getElementsByName(questionName);
        let selected = null;
        for (const option of options) {
            if (option.checked) {
                selected = option.value;
                break;
            }
        }

        if (selected === correct) {
            score++;
        }
    });

    const participantName = document.getElementById("participant-name").value;
    const startTimeStr = quizStartTime.toISOString().slice(0, 19).replace('T', ' ');

    try {
        const response = await fetch('/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: participantName,
                score: score,
                start_time: startTimeStr
            })
        });

        if (!response.ok) throw new Error('Lỗi lưu dữ liệu');

        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = `Bạn <strong>${participantName}</strong> trả lời đúng ${score} / ${questions.length} câu hỏi!`;

        disableQuiz(true);

        // Vô hiệu hóa nút nộp bài
        const submitBtn = document.getElementById("submit-btn");
        submitBtn.disabled = true;
        submitBtn.style.opacity = "0.5";
    } catch (err) {
        alert("Không thể lưu kết quả, vui lòng thử lại sau.");
    }
}
