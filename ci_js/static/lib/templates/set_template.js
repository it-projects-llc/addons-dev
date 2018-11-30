function ${name}() {
    return [
    % for step in step_ids:
        {
        % if step.content:
        content: '${step.content}',
        % endif
        trigger: '${step.trigger}',
        % if step.extra_trigger:
        extra_trigger: '${step.extra_trigger}',
        % endif
        % if step.timeout:
        timeout: ${step.timeout},
        % endif
        % if step.position:
        position: '${step.position}',
        % endif
        % if step.width:
        width: ${step.width},
        % endif
        % if step.edition and step.edition != 'both':
        edition: '${step.edition}',
        % endif
        % if step.run:
        run: '${step.run}',
        % endif
        % if step.auto:
        auto: true,
        % endif
        },
        % endfor
    ];
}
