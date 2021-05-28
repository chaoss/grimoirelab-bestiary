import gql from "graphql-tag";

const projectFragment = gql`
  fragment projectFields on ProjectType {
    id
    name
    title
    ecosystem {
      id
      name
    }
    parentProject {
      name
      parentProject {
        name
        parentProject {
          name
        }
      }
    }
  }
`;

const GET_ECOSYSTEMS = gql`
  query GetEcosystems($pageSize: Int, $page: Int) {
    ecosystems(pageSize: $pageSize, page: $page) {
      entities {
        id
        name
        title
        description
        projectSet {
          ...projectFields
          subprojects {
            ...projectFields
            subprojects {
              ...projectFields
              subprojects {
                ...projectFields
              }
            }
          }
        }
      }
      pageInfo {
        totalResults
      }
    }
  }
  ${projectFragment}
`;

const GET_BASIC_PROJECT_INFO = gql`
  query GetBasicInfo($pageSize: Int, $page: Int, $filters: ProjectFilterType) {
    projects(pageSize: $pageSize, page: $page, filters: $filters) {
      entities {
        id
        title
      }
    }
  }
`;

const GET_PROJECTS = gql`
  query GetProjects($pageSize: Int, $page: Int, $filters: ProjectFilterType) {
    projects(pageSize: $pageSize, page: $page, filters: $filters) {
      entities {
        ...projectFields
        subprojects {
          ...projectFields
          subprojects {
            ...projectFields
            subprojects {
              ...projectFields
            }
          }
        }
      }
      pageInfo {
        page
        numPages
      }
    }
  }
  ${projectFragment}
`;

const GET_PROJECT_BY_NAME = gql`
  query getProjectById($filters: ProjectFilterType) {
    projects(pageSize: 1, page: 1, filters: $filters) {
      entities {
        ...projectFields
        subprojects {
          ...projectFields
          subprojects {
            ...projectFields
            subprojects {
              ...projectFields
            }
          }
        }
      }
    }
  }
  ${projectFragment}
`;

const getEcosystems = (apollo, pageSize, page) => {
  const response = apollo.query({
    query: GET_ECOSYSTEMS,
    variables: {
      pageSize,
      page
    },
    fetchPolicy: "no-cache"
  });
  return response;
};

const GetBasicProjectInfo = (apollo, pageSize, page, filters) => {
  const response = apollo.query({
    query: GET_BASIC_PROJECT_INFO,
    variables: {
      pageSize,
      page,
      filters
    }
  });
  return response;
};

const getProjects = (apollo, pageSize, page, filters) => {
  const response = apollo.query({
    query: GET_PROJECTS,
    variables: {
      pageSize,
      page,
      filters
    }
  });
  return response;
};

const getProjectByName = (apollo, name, ecosystemId) => {
  const response = apollo.query({
    query: GET_PROJECT_BY_NAME,
    variables: {
      filters: {
        ecosystemId: ecosystemId,
        name: name
      }
    },
    fetchPolicy: "no-cache"
  });
  return response;
};

export { getEcosystems, GetBasicProjectInfo, getProjects, getProjectByName };
