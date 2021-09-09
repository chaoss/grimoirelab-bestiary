const getProjectBreadcrumbs = project => {
  const breadcrumbs = [
    {
      text: project.name,
      disabled: true
    }
  ];

  function findParents(parent, ecosystem) {
    if (parent) {
      breadcrumbs.splice(0, 0, {
        text: parent.name,
        to: `/ecosystem/${ecosystem.id}/project/${parent.name}`,
        exact: true
      });
      findParents(parent.parentProject, ecosystem);
    } else {
      breadcrumbs.splice(0, 0, {
        text: ecosystem.name,
        href: `/ecosystem/${ecosystem.id}`
      });
    }
  }

  findParents(project.parentProject, project.ecosystem);

  return breadcrumbs;
};

const getViewBreadCrumbs = (view, ecosystem, parent) => {
  if (ecosystem) {
    const project = {
      name: view,
      ecosystem: {
        id: ecosystem.id,
        name: ecosystem.name
      },
      parentProject: parent
    };
    return getProjectBreadcrumbs(project);
  } else {
    return [{ text: view, disabled: true }];
  }
};

export { getProjectBreadcrumbs, getViewBreadCrumbs };
