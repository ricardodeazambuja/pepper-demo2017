<?xml version="1.0" encoding="UTF-8" ?>
<Package name="iSpyGame" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="iSpy" src="iSpy/iSpy.dlg" />
        <Dialog name="MartaDialog" src="MartaDialog/MartaDialog.dlg" />
    </Dialogs>
    <Resources>
        <File name="index" src="html/index.htm" />
        <File name="marta_splash" src="html/marta_splash.jpg" />
        <File name="icon" src="icon.png" />
    </Resources>
    <Topics>
        <Topic name="iSpy_enu" src="iSpy/iSpy_enu.top" topicName="iSpy" language="en_US" />
        <Topic name="MartaDialog_enu" src="MartaDialog/MartaDialog_enu.top" topicName="MartaDialog" language="en_US" />
    </Topics>
    <IgnoredPaths>
        <Path src=".metadata" />
    </IgnoredPaths>
</Package>
