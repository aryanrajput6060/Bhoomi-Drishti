# Reads the visible text of windows through UI Automation — exact strings as the
# accessibility layer reports them (works for native Win32/WPF/UWP apps).
# Returns JSON: { windows: [...], elements: [ { window, type, name, value } ] }
[CmdletBinding()]
param(
    [string]$TitleLike = "",
    [int]$MaxElements = 500
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$AutomationElement = [System.Windows.Automation.AutomationElement]
$treeWalker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
$trueCondition = [System.Windows.Automation.Condition]::TrueCondition

function Get-RootElements {
    param([string]$Title)
    if ([string]::IsNullOrWhiteSpace($Title)) {
        $condition = New-Object System.Windows.Automation.AndCondition(
            (New-Object System.Windows.Automation.PropertyCondition($AutomationElement::ControlTypeProperty, [System.Windows.Automation.ControlType]::Window)),
            (New-Object System.Windows.Automation.PropertyCondition($AutomationElement::IsOffscreenProperty, $false))
        )
        return @($AutomationElement::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $condition))
    }
    $condition = New-Object System.Windows.Automation.PropertyCondition($AutomationElement::NameProperty, $Title)
    $match = @($AutomationElement::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $condition))
    if ($match.Count -eq 0) {
        $all = @($AutomationElement::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $trueCondition))
        $match = @($all | Where-Object { $_.Current.Name -like "*$Title*" })
    }
    return $match
}

function Read-ElementText {
    param($Element)
    try {
        $pattern = $null
        if ($Element.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$pattern)) {
            $value = $pattern.Current.Value
            if (-not [string]::IsNullOrWhiteSpace($value)) { return $value }
        }
    }
    catch { }
    return ""
}

$roots = Get-RootElements -Title $TitleLike
$elements = @()
$windows = @()
$budget = $MaxElements

foreach ($root in $roots) {
    $title = $root.Current.Name
    if ([string]::IsNullOrWhiteSpace($title)) { continue }
    $windows += [pscustomobject]@{ title = $title; pid = $root.Current.ProcessId }

    $queue = New-Object System.Collections.Queue
    $queue.Enqueue($root)
    while ($queue.Count -gt 0 -and $budget -gt 0) {
        $current = $queue.Dequeue()
        $child = $treeWalker.GetFirstChild($current)
        while ($null -ne $child -and $budget -gt 0) {
            $budget--
            $queue.Enqueue($child)
            try {
                $name = $child.Current.Name
                $value = Read-ElementText -Element $child
                $type = $child.Current.ControlType.ProgrammaticName -replace '^ControlType\.', ''
                if ($type -in @('Text', 'Edit', 'Document', 'Button', 'ListItem', 'MenuItem', 'Hyperlink', 'TabItem', 'ComboBox', 'CheckBox') ) {
                    if (-not [string]::IsNullOrWhiteSpace($name) -or -not [string]::IsNullOrWhiteSpace($value)) {
                        $elements += [pscustomobject]@{
                            window = $title
                            type   = $type
                            name   = $name
                            value  = $value
                        }
                    }
                }
            }
            catch { }
            $child = $treeWalker.GetNextSibling($child)
        }
    }
}

[pscustomobject]@{
    windows  = $windows
    elements = $elements
} | ConvertTo-Json -Depth 6 -Compress