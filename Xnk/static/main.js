import Calendar from 'tui-calendar'; /* ES6 */
import "../node_modules/tui-calendar/dist/tui-calendar.css";

// If you use the default popups, use this.
// import 'tui-date-picker/dist/tui-date-picker.css';
// import 'tui-time-picker/dist/tui-time-picker.css';
var calendar = new Calendar('#calendar', {
      defaultView: 'month',
      taskView: true,
      template: {
              monthDayname: function(dayname) {
                        return '<span class="calendar-week-dayname-name">' + dayname.label + '</span>';
                      }
            }
});
