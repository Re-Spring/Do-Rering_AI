// 웹 페이지의 모든 컨텐츠가 로드되고 준비된 후에 실행됩니다.
document.addEventListener("DOMContentLoaded", function () {
  // "storyForm"이라는 ID를 가진 폼이 제출될 때의 이벤트 리스너를 추가합니다.
  document.getElementById("storyForm").addEventListener("submit", function (e) {
    console.log("버튼 눌렀어용");
    e.preventDefault(); // 폼의 기본 제출 동작을 막습니다. 즉, 페이지가 새로고침되지 않습니다.

    // 폼 데이터를 기반으로 FormData 객체를 생성합니다.
    var formData = new FormData(e.target); // e.target은 이벤트가 발생한 폼을 가리킵니다.
    var story = {};

    // FormData의 각 항목을 순회하며 storyData 객체에 추가합니다.
    for (var pair of formData.entries()) {
      story[pair[0]] = pair[1];
      console.log(story[pair[0]]);
    }

    // "/generate-story" 경로로 POST 요청을 보냅니다. 이는 서버에 이야기를 생성하도록 요청하는 것입니다.
    fetch("/generate-story", {
      method: "POST", // HTTP 메소드를 POST로 설정합니다.
      headers: {
        "Content-Type": "application/json", // 요청의 컨텐츠 타입을 JSON으로 지정합니다.
      },
      body: JSON.stringify(story), // 폼 데이터를 포함한 객체를 JSON 문자열로 변환
    })
      .then(console.log("fetch 나옴"))
      .then((response) => response.json()) // 응답을 JSON 형태로 변환합니다.
      .then((data) => {
        const storyDiv = document.getElementById("storyOutput"); // 결과를 표시할 div 요소를 찾습니다.
        storyDiv.innerHTML = ""; // 기존에 div 내에 있던 내용을 모두 지웁니다.

        // 받아온 데이터의 각 키(key)를 순회하면서, 각 키에 해당하는 값을 담은 <p> 태그를 생성하고 div에 추가합니다.
        Object.keys(data).forEach((key) => {
          const para = document.createElement("p");
          para.textContent = data[key]; // <p> 태그의 내용을 설정합니다.
          storyDiv.appendChild(para); // 생성된 <p> 태그를 storyDiv에 추가합니다.
          story[key] = data[key];
          console.log("key 값 : ", key);
          // console.log("value값 : ", story[key]);
        });
        console.log("story : " + story);
        // makePictures(story);
        console.log(Object.keys(story).length);
      })
      .catch((error) => console.error("Error:", error)); // 오류가 발생하면 콘솔에 에러를 기록합니다.
  });
});

function makePictures(story) {
  console.log("makePictures story");
  console.log(story);
  var input_text = story;
  // console.log("input_text : " + input_text);
  if (Object.keys(input_text).length > 0) {
    console.log("fetch");
    fetch("/mkimg", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompts: input_text,
      }),
    })
      .then((response) => {
        console.log("then 1");
        // console.log("response : " + response);
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log("then 2");
        var outputImage = document.getElementById("output_image");
        if (outputImage && data.image_path) {
          outputImage.src = data.image_path + "?" + new Date().getTime();
        }
      })
      .catch((error) => {
        console.error("Fetch 동작 에러:", error);
      });
  } else {
    console.log("story 없음");
  }
}

function chknum() {
  var inputElement = document.getElementById("page");
  var value = inputElement.value;

  if (value < 6 || value > 9) {
    alert("6~9에 해당하는 값만 입력해주세요.");
    inputElement.value = ""; // 입력 필드를 비웁니다.
    return false;
  }
  return true;
}
