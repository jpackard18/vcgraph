var graphElement = document.getElementById('graph');
graphElement.addEventListener('touchenter', (event) => PlotlyPage.touchHandler(event));
graphElement.addEventListener('touchleave', (event) => PlotlyPage.touchHandler(event));
graphElement.addEventListener('touchstart', (event) => touchHandler(event));
graphElement.addEventListener('touchmove', (event) => touchHandler(event));
graphElement.addEventListener('touchend', (event) => touchHandler(event));

function touchHandler(event)
{
    var touches = event.changedTouches,
        first = touches[0],
        type = "";
    switch(event.type)
    {
      case "touchenter": type = "mouseover"; break;
      case "touchleave": type = "mouseout";  break;
      case "touchstart": type = "mousedown"; break;
      case "touchmove":  type = "mousemove"; break;
      case "touchend":   type = "mouseup";   break;
      default:           return;
    }

    var opts = {
      bubbles: true,
      screenX: first.screenX,
      screenY: first.screenY,
      clientX: first.clientX,
      clientY: first.clientY,
    };

    var simulatedEvent = new MouseEvent(type, opts);

    first.target.dispatchEvent(simulatedEvent);
    event.preventDefault();
}