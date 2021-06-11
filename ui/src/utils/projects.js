const getRoot = project => {
  const parent = project ? project.parentProject : null;
  if (parent) {
    project = getRoot(parent);
  }
  return project;
};

const hasSameRoot = (project, fromProject) => {
  if (project.parentProject) {
    return getRoot(project.parentProject).name === getRoot(fromProject).name;
  }
  return true;
};

const isDescendant = (project, fromProject) => {
  const queue = [fromProject];
  while (queue.length > 0) {
    const current = queue.pop(0);
    if (current.subprojects) {
      for (let subproject of current.subprojects) {
        if (subproject.id == project.id) {
          return true;
        }
        queue.push(subproject);
      }
    }
  }
};

const isParent = (project, fromProject) => {
  return project.parentProject
    ? fromProject.name === project.parentProject.name
    : false;
};

export { getRoot, hasSameRoot, isDescendant, isParent };
