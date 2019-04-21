$(".datepicker-input").datepicker({ language: 'es', format: "yyyy/mm/dd" });

$(document).ready(function () {
  console.log('notifications');
  downloadCompleted = 0;
  downloadRunning = 0;
  extractCompleted = 0;
  extractRunning = 0;
  
  setInterval(function () {
    $.ajax({
      url: "/get_notifications/",
      type: 'GET',
      data: { 'check': true },
  
      success: function (json) {
        if (json.result) {
          if (downloadCompleted != 0 && extractCompleted != 0) {
            if (downloadCompleted != json.download_completed) {
              $('#alerts').append('<p>' + (json.download_completed - downloadCompleted) + ' tarea(s) de descarga ha(n) finalizado.</p>');
            }
            if (extractCompleted != json.extract_completed) {
              $('#alerts').append('<p>' + (json.extract_completed - extractCompleted) + ' tarea(s) de extracción ha(n) finalizado.</p>');
            }
          }
          downloadCompleted = json.download_completed;
          downloadRunning = json.download_running;
          extractCompleted = json.extract_completed;
          extractRunning = json.download_running;
        }
      }
    });
  }, 5000);

  setInterval(function() {
    $('#alerts').html("");
  }, 15000);
});