# LaundryDetector
---

This is a simple service that notifies users via SMS when a washer or dryer appliance has finished its cycle. It allows users to go on about their day
after starting a load of laundry, and not have to worry about staying within earshot of the laundry room.

1. [Overview](#overview)
2. [TO-DO](#todo)
3. [License](#license)

---

## <a id="overview"></a>Overview

This document provides details on how LaundryDetector works, including configurable parameters to customize for each user's unique situations.
It also includes a [To-Do](#ToDo) section that briefly goes over what still needs to get done, as well as design goals for the project.

### sub-heading


## TO-DO

1. **More accurate logic**
The decision-making, ("washer has started/finished") including false alarm detection needs to be improved. I designed the program based on the assumption
that within a washer/dryer cycle, vibration would be *constant*. The false alarm detection was only for dealing with the lapses in vibration *between* cycles.
I need to implement a more robust system that 1) isn't triggering a ton of false alarms (like now), and 2) persists through the small and frequent lapses
in vibration throughout the entire wash/dry loop.

2. **Settings file**
I'd like to incorporate an external settings file that LaundryDetector.py can reference for initializing variables, like pin, min_start/stop_delta, aws stuff, etc.
I just don't know how to do this yet, but I'm sure it's not too difficult (though I probably just jinxed myself...).

3. **UI for changing Settings**
Even if it's just a simple bash shell UI with numbered options. Once I have the framework in place, I can expand from there as needed.

4. **Project Restructuring**
This is my first major application development project, so I'm sure I haven't properly set up things like file/folder hierarchy, project-level
global variables, etc., as referenced in [this excellent StackExchange answer](https://stackoverflow.com/a/43794480/4166505) by what appears to be someone very experienced in large projects.

5. **Test other attachment methods *(?)***
I have a feeling the adhesive velcro dampens the vibrations reaching the sensor, because during a wash loop it only detected vibration during the final
spin cycle. And on the dryer loop, it would detect starting, then detect starting again without detecting stopping first (though that may be a design flaw...).

6. **Use different detection mechanism *(?)***
Honeslty, I'm not a big fan of vibration as the sole detection method- it's extremely indirect and exposed to a multitude of 3rd party interference. It was just the quickest
and easiest solution to get this project on the road. First alternative that pops into my head is measuring amp levels, assuming that when washing/drying there is a noticeable increase from idle.
But I'll have to do more research of course, and make sure I find something that is common across appliances from all manufacturers and form factors.

## License

idfk which [license](https://choosealicense.com/) to [pick](https://www.cio.com/article/2382115/open-source-tools/how-to-choose-the-best-license-for-your-open-source-software-project.html), so I'm just going to leave it "unlicensed" for now (which theoretically *forbids* anyone from using it at all).
This is really a non-issue at this early stage anyway, but I thought I'd at least include it in the README.
