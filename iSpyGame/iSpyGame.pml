<?xml version="1.0" encoding="UTF-8" ?>
<Package name="Working" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="." xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="MartaDialog" src="MartaDialog/MartaDialog.dlg" />
        <Dialog name="iSpyDialog" src="iSpyDialog/iSpyDialog.dlg" />
    </Dialogs>
    <Resources>
        <File name="icon" src="icon.png" />
        <File name="marta_splash" src="html/marta_splash.jpg" />
        <File name="index" src="html/index.htm" />
        <File name="image" src="html/image.jpg" />
    </Resources>
    <Topics>
        <Topic name="MartaDialog_enu" src="MartaDialog/MartaDialog_enu.top" topicName="MartaDialog" language="en_US" />
        <Topic name="iSpyDialog_enu" src="iSpyDialog/iSpyDialog_enu.top" topicName="iSpyDialog" language="en_US" />
    </Topics>
    <IgnoredPaths />
</Package>
